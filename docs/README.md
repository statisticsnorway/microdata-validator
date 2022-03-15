## BESKRIVELSE AV METADATAMODELLEN
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
* **shortName**: Teknisk navn på enhetstypen.
* **name**: Menneskelig lesbart navn på enhetstypen.
* **description**: Beksrivelse av enhetstypen.


## VALIDERING

### UTFORMING AV DATA
En datafil skal levers som en csv-fil med semikolon som kolonneseparator. Det skal alltid være 5 kolonner i denne rekkefølgen:
1. identifikator
2. verdi
3. start
4. stop
5. tom kolonne (Denne kolonnen er holdt av om det skulle være behov for en ekstra attributtvariabel i datasettet. Eksempel: datakilde)

```
12345678910;100000;2020-01-01;2020-12-31;
12345678910;200000;2021-01-01;2021-12-31;
12345678911;100000;2018-01-01;2018-12-31;
12345678911;150000;2020-01-01;2020-12-31;
```

Dette er et eksempel på et dataset som beskriver personer sin inntekt over tidsperioder. Kolonnene kan beskrives slik:
* Identifikator: fødselsnummer
* Verdi: Akkumulert lønn i tidsperioden
* Start: start på tidsperioden
* Stopp: slutt på tidsperioden
* Tom kolonne (Denne kolonnen er holdt av om det skulle være behov for en ekstra attributtvariabel i datasettet. Det er ikke behov for denne kolonnen i dette datasettet, og den er derfor tom.)

### GENERELLE VALIDERINGSREGLER FOR DATA
* Det kan ikke oppstå tomme rader i datasettet
* En rad kan ikke være lenger en 5 elementer
* Hver rad må ha en identifikator
* Hver rad må ha en verdi
* Verdier som oppstår i start og stopp kolonnene må ha riktig datoformat "yyyy-mm- dd" ex.: 2020-12-31
* Datafilen må være utf-8 enkodet

### VALIDERINGSREGLER FOR TEMPORALITY TYPE
* **FIXED** (Fast/konstant verdi, f.eks. fødeland)
    - Alle rader må ha en unik identifikator
* **STATUS** (tverrsnitt, dvs. måling på et gitt tidspunkt)
    - Må ha en startdato
    - Må ha en stoppdato
    - Start og stop kolonnene skal ha samme verdi for en gitt rad
* **ACCUMULATED** (akkumulert for en periode f.eks. årsinntekt)
    - Må ha en startdato
    - Må ha en stoppdato
    - Start kan ikke være større en stopp
* **EVENT** (Forløpsdata med gyldighetsperiode)
    - Må ha en startdato
    - Start kan ikke være større en stopp, om en ikke-tom stopp verdi finnes i samme rad
    - En ny rad kan ikke legges til for samme identifikator hvis den forrige raden ikke har en stoppdato
    - startdato må være større en forrige rads stoppdato for samme identifikator 
