## BESKRIVELSE AV METADATAMODELLEN
_______
I tillegg til de vedlagte eksemplene på metadata som json-filer, beskriver dette dokumentet feltene i modellen. Det anbefales å lese begge deler for å forstå modellen.

### ROTNIVÅFILTER
Disse feltene omhandler datasettet som helhet.
* **shortName**: Navnet på datasettet
* **temporalityType**: temporalitetstypen for datasettet kan være en av FIXED, ACCUMULATED, STATUS og EVENT.
* **spatialCoverageDescription**: Det geograftiske området der data er aktuelle.
* **populationDescription**: Beskrivelse av populasjonen i datasettet.


### DATAREVISION
Disse feltene omhandler den aktuelle versjonen av datasettet.
* **description**: Beskrivelse av denne versjonen av datasettet.
* **temporalEndOfSeries**: Er dette siste oppdatering av data for dette datasettet? [True | False]

### IDENTIFIER VARIABLES
Beskrivelse av identifikator-kolonnene. Det er en liste i modellen, men det støttes for øyeblikket kun 1 identifikator i microdata plattformen.
* **shortName**: Teknisk navn på verdikolonnen. Eksempel: "PERSONID_1".
* **name**: Navn på typen identifikator. Eksempel: "Personidentifikator".
* **description**: Beskrivelse av innholdet i kolonnen. Eksempel: "Pseudonymisert fødselsnummer"
* **dataType**: DataType for verdiene. En av ["STRING", "LONG"]
* **format**: Nærmere definisjon av datatypen. For eksempel et regular expression.
* **uriDefinition**: Lenke til ekstern ressurs med definisjon for variablen.
* **unitType**: Se definisjonen under.
* **valueDomain**: se definisjonen under.

### MEASURE VARIABLES
Beskrivelse av verdi-kolonnen for målte verdier. Det er en liste i modellen, men det støttes for øyeblikket kun 1 verdi-kolonne i microdata plattformen.
* **shortName**: Teknisk navn på verdikolonnen. Brukes som variabelnavn i ROSE- klienten. Eksempel: INNTEKT_AKSJEUTBYTTE.
* **name**: Navn(Tittel) på verdikolonnen. Brukes som kolonnenavn i ROSE-klienten. Eksempel: "Aksjeutbytte".
* **description**: Beskrivelse av kolonnen. Eksempel: "Skattepliktig og skattefritt utbytte i... "
* **dataType**: Datatype for verdiene. En av ["STRING", "LONG", "DOUBLE", "DATE"]
* **format**: Nærmere definisjon av datatypen. For eksempel et regular expression.
* **uriDefinition**: Lenke til ekstern ressurs med definisjon for variablen.
* **unitType**: Se definisjonen under.
* **valueDomain**: Se definisjonen under.

### ATTRIBUTE VARIABLES
Beskrivelse av attributt-kolonnene. Til å begynne med trenger man kun forholde seg til START_TIME og STOP_TIME
* **variableRole**: En av ["START_TIME", "STOP_TIME"]
* **shortName**: Teknisk navn på attributt-kolonnen.
* **name**: Navn på attributt-kolonnen. Brukes som kolonnenavn i ROSE-klienten.
* **description**: Beskrivelse av kolonnen.
* **dataType**: Datatype for verdiene. En av ["STRING", "LONG", "DOUBLE", "DATE"]
* **format**: Nærmere definisjon av datatypen. For eksempel et regular expression.
* **uriDefinition**: Lenke til ekstern ressurs med definisjon for variablen.
* **unitType**: Se definisjonen under.
* **valueDomain**: Se definisjonen under.


### VALUE DOMAIN
Value domain beskriver verdiområdet til variable. Enten i form av kodeverk(codeList), eller som en beskrivelse av forventede verdier.
* **description**: En beskrivelse av domenet. Eksempel for variablen brutto-inntekt: "Alle positive tall".
* **measurementUnitDescription**: En beskrivelse av enheten som måles i domenet. Eksempel: "Norske kroner"
* **measurementType**: En maskinlesbar definisjon av enheten som måles. En av CURRENCY, WEIGHT, LENGTH, HEIGHT eller GEOGRAPHICAL
* **uriDefinition**: Lenke til ekstern ressurs med definisjon for domenet.
* **codeList**: En kodeliste med valide koder for domenet, og beskrivelser av disse kodene.
* **sentinelAndMissingValues**: En kodeliste med koder som representerer manglende
verdier eller invalide verdier som man fortsatt forventer at skal eksistere i datasettet. Eksempelvis kode "0" for "ukjent verdi".


Her er to eksempler på to relativt forskjellige valuedomains.
Første eksempel er for et datasett med personer sin inntekt akkumulert over et år om gangen. Dette er measureVariable sitt valueDomain:
```json
"valueDomain": {
    "uriDefinition": [],
    "description": [{"languageCode": "no", "value": "Årlig personinntekt"}],
    "measurementType": "CURRENCY",
    "measurementUnitDescription": [{"languageCode": "no", "value": "Norske Kroner"}]
}
```

Andre Eksempel er et datasett som beskriver kjønn for en befolkning. Dette er measureVariable sitt valueDomain:
```json
"valueDomain": {
    "uriDefinition": [],
    "description": [{"languageCode": "no", "value": "Variablen viser personens kjønn"}],
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

Her forventer vi at alle verdier i kolonnen skal være enten 1 eller 2, da disse kodene refererer til Mann og Kvinne. Vi har også en sentinelverdi som vil oppstå, som vi forventer og ikke skal sees på som en feil i datasettet.


### UNIT TYPE
Beskrivelse av enheten data er bundet til. Et fødselsnummer kan brukes for å identifisere enheten PERSON. Et annet eksempel vil være et organisasjonsnnummer som er identifiserende variabel med enhetstype FORETAK.

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