## BESKRIVELSE AV EKSEMPELDATA
______
### SYNT_PERSON_INNTEKT
Dette datasettet inneholder syntetisk data om personer sin årlige inntekt.
Strukturen av en rad er nærmere beskrevet i metadata, men kan summeres opp slik:

        PERSON_ID;INNTEKT;START;STOP

Temporalitetstypen på dette datasettet er "ACCUMULATED". Det betyr at når vi har en rad som,

        00000000000001;1000;2020-01-01;2020-12-31;

betyr det at inntekten til en person(00000000000001) akkumulert fra starten til slutten av 2020 var 1000 kroner.
Vi kan ha flere rader med samme person, men disse radene må beskrive forskjellige, ikke- overlappende tidsspenn for den personen.
&nbsp;

&nbsp; 



### SYNT_PERSON_KJOENN
Dette datasettet innholder info om kjønn til en befolkning.
Strukturen av en rad er nærmere beskrevet i metadata, men kan summeres opp slik:

        PERSON_ID;KJØNN;START;STOP

Vi skriver ikke "Mann" og "Kvinne" i raden, men bruker heller en kodeliste man kan finne beskrevet i metadata. I raden står det enten 1 eller 2, for "Mann" eller "Kvinne".

        00000000000001;1;;2020-01-01

Temporalitetstypen til dette datasettet er "FIXED". Det betyr at tilstanden har blitt innhentet på et tidspunkt og forandrer seg ikke. Vi trenger derfor ikke legge tidsspenn i en rad med data. Vi bruker STOP kolonnen til å beskrive når dataen ble hentet. Vi vet da at raden i alle fall er gyldig frem til datoen den ble uthentet.
&nbsp;

&nbsp; 


### SYNT_BEFOLKNING_SIVSTAND
Dette Datasettet inneholder info om sivilstand til en befolkning. Strukturen av en rad er nærmere beskrevet i metadata, men kan summeres opp slik:

        PERSON_ID;SIVILSTAND;START;STOP

I likhet med SYNT_BEFOLKNING_KJOENN har vi her sivilstand basert på en kodeliste. Men her er det ikke alle kodene som er gyldige for alle tidsspenn. Som vi ser i metadata er det ikke noe gyldig kode 6 ("Registrert partner") før 1927.
Temporalitetstypen her er "EVENT". Vi krever da en START dato. Om det ikke står noe stop-dato er antagelsen at den tilstanden er sann frem til dagens dato.
Hvis kode 1 betyr gift, og 2 betyr ugift:

        000000000000001;2;1980-01-01;1999-12-31;
        000000000000001;1;2000-01-01;;

Personen beskrevet her var da ugift fra 1980, og ble gift i år 2000, og er fortsatt gift i dag. Det er derfor viktig at ikke rader for samme person overlapper i tidsrommet.
&nbsp;

&nbsp; 

