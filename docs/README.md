## THE METADATA MODEL
_______
In addition to the examples of metadata json files present in this repository, this document briefly describes the fields in the metadata model.
### ROOT LEVEL FIELDS
These fields describe the dataset as a whole.
* **shortName**: Name of the dataset
* **temporalityType**: The temporality type of the dataset. Must be one of FIXED, ACCUMULATED, STATUS og EVENT.
* **spatialCoverageDescription**: The geographic area relevant to the data.
* **populationDescription**: Description of the dataset's population.


### DATAREVISION
These fields describe the current version of the dataset.
* **description**: Description of this version of the dataset.
* **temporalEndOfSeries**: Is this the final updates for this dataset? [True | False]

### IDENTIFIER VARIABLES
Description of the indentifier column of the dataset. It is represented as a list in the metadata model, but currently only one identifier is allowed per dataset.
* **shortName**: Machine readable name for the identifier column. Example: "PERSONID_1".
* **name**: Human readable name for the identifier colum. Example: "Personidentifikator".
* **description**: Description of the column contents. Example: "Pseudonymisert fødselsnummer"
* **dataType**: DataType for the values in the column. One of: ["STRING", "LONG"]
* **format**: More detailed description of the values. For example a regular expression.
* **uriDefinition**: Link to external resource describing the identifier.
* **unitType**: See definition below.
* **valueDomain**: See definition below.

### MEASURE VARIABLES
Description of the measure column of the dataset. It is represented as a list in the metadata model, but currently only one measure is allowed per dataset.
* **shortName**: Machine readable name for the measure. Is also used as variable name in the ROSE- client. Example: INNTEKT_AKSJEUTBYTTE.
* **name**: Human readable name(Label) of the measure column. Used as the column label in the ROSE-klienten. Example: "Aksjeutbytte".
* **description**: Description of the column contents. Example: "Skattepliktig og skattefritt utbytte i... "
* **dataType**: DataType for the values in the column. One of: ["STRING", "LONG", "DOUBLE", "DATE"]
* **format**: More detailed description of the values. For example a regular expression.
* **uriDefinition**: Link to external resource describing the measure.
* **unitType**: See definition below.
* **valueDomain**: See definition below.

### ATTRIBUTE VARIABLES
Description of the attribute columns. For now the only valid values are START_TIME og STOP_TIME
* **variableRole**: One of: ["START_TIME", "STOP_TIME"]
* **shortName**: Machine readable name for the measure. 
* **name**: Human readable name(Label) of the attribute column. Used as the column label in the ROSE-klienten. Example: "Startdato".
* **description**: Description of the column contents.
* **dataType**: DataType for the values in the column. One of: ["STRING", "LONG", "DOUBLE", "DATE"]
* **format**: More detailed description of the values. For example a regular expression.
* **uriDefinition**: Link to external resource describing the measure.
* **unitType**: See definition below.
* **valueDomain**: See definition below.


### VALUE DOMAIN
Describes the Value domain for the relevant variable. Either by codeList(enumarated value domain), or a description of expected values(described value domain).
* **description**: A description of the domain. Example for the variable "BRUTTO_INNTEKT": "Alle positive tall".
* **measurementUnitDescription**: A description of the unit measured. Example: "Norske Kroner"
* **measurementType**: A machine readable definisjon of the unit measured. One of: [CURRENCY, WEIGHT, LENGTH, HEIGHT, GEOGRAPHICAL]
* **uriDefinition**: Link to external resource describing the domain.
* **codeList**: A code list of valid codes for the domain, description, and their validity period.
* **sentinelAndMissingValues**: A code list where the codes represent missing or sentinel values that, while not entirely valid, are still expected to appear in the dataset. Example: Code 0 for "Unknown value".


Here is an example of two different value domains.
The first value domain belongs to a measure for dataset where the measure is a persons accumulated gross income:
```json
"valueDomain": {
    "uriDefinition": [],
    "description": [{"languageCode": "no", "value": "Norske Kroner"}],
    "measurementType": "CURRENCY",
    "measurementUnitDescription": [{"languageCode": "no", "value": "Norske Kroner"}]
}
```
This example is what we would call a __described value domain__.

The second example belongs to the measure variable of a dataset where the measure describes the gender of a population:
```json
"valueDomain": {
    "uriDefinition": [],
    "codeList": [
        {
            "code": "1",
            "categoryTitle": [{"languageCode": "no", "value": "Mann"}],
            "validFrom": "1900-01-01"
        },
        {
            "code": "2",
            "categoryTitle": [{"languageCode": "no", "value": "Kvinne"}],
            "validFrom": "1900-01-01"
        }
    ],
    "sentinelAndMissingValues": [
        {
            "code": "0",
            "categoryTitle": [{"languageCode": "no", "value": "Ukjent"}],
            "validFrom": "1900-01-01"
        }
    ]
}
```
We expect all values in this dataset to be either "1" or "2", as this dataset only considers "Male" or "Female". But we also expect a code "0" to be present in the dataset, where it represents "Unknown". A row with "0" as measure is therefore not considered invalid. A value domain with a code list like this is what we would call an __enumarated value domain.


### UNIT TYPE
Description of the unit the data describes. A "fødselsnummer" can be used to identify a PERSON. Another example would be an "organisasjonsnummer" that would be used to identify a "FORETAK".
* **shortName**: Machine readable name.
* **name**: Human readable name.
* **description**: Description of the unit type.


## VALIDATION

### CREATING A DATAFILE
A data file must be supplied as a csv file with semicolon as the column seperator. There must always be 5 columns present in this order:
1. identifier
2. measure
3. start
4. stop
5. empty column (This column is reserved for an extra attribute variable if that is considered necessary. Example: Datasource)

Example:
```
12345678910;100000;2020-01-01;2020-12-31;
12345678910;200000;2021-01-01;2021-12-31;
12345678911;100000;2018-01-01;2018-12-31;
12345678911;150000;2020-01-01;2020-12-31;
```

This dataset describes a group of persons gross income accumulated yearly. The columns can be described like this:
* Identifier: fødselsnummer
* Measure: Accumulated gross income for the time period
* Start: start of time period
* Stopp: end of time period
* Empty column (This column is reserved for an extra attribute variable if that is considered necessary. As there is no need here, it remains empty.)

### GENERAL VALIDATIONRULES FOR DATA
* There can be no empty rows in the dataset
* There can be no more than 5 elements in a row
* Every row must have a non-empty identifier
* Every row must have a non-empty measure
* Values in the stop- and start-columns must be formatted correctly: "YYYY-MM-DD". Example "2020-12-31".
* The data file must be utf-8 encoded

### VALIDATIONRULES BY TEMPORALITY TYPE
* **FIXED** (Constant value, ex.: place of birth)
    - All rows must have an unique identifier. (No repeating identifiers within a dataset)
* **STATUS** (measurement taken at a certain point in time. (cross section))
    - Must have a start date
    - Must have a stop date
    - Start and stop date must be equal for any given row
* **ACCUMULATED** (Accumulated over a period. Ex.: yearly income)
    - Must have a start date
    - Must have a stop date
    - Start can not be later than stop
    - Time periods for the same identifiers must not intersect
* **EVENT** (Forløpsdata med gyldighetsperiode)
    - Must have a start date
    - Start can not be later than stop, if there is a non empty stop column in the same row
    - Time periods for the same identifiers must not intersect (A row without a stop date is considered an ongoing event, and will intersect with all timespans after its start date)
