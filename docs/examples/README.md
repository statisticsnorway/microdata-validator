## DATASET EXAMPLES
______
### SYNT_PERSON_INNTEKT
This dataset contains synthetic data describing the yearly income of a group of persons.
The structure of a row in the data is described well by the metadata, but simply put:
        
        PERSON_ID;INCOME;START;STOP

The temporality type of this dataset is "ACCUMULATED". Meaning that when we have a row:

        00000000000001;1000;2020-01-01;2020-12-31;

It means that the income of a person(00000000000001) accumulated through 2020 is 1000 NOK.
We can have several rows for the same person, but these rows must describe different, non-intersecting timespans.
&nbsp;

&nbsp; 

### SYNT_PERSON_KJOENN
This dataset contains synthetic data describing recorded gender of group of persons.
The structure of a row in the data is described well by the metadata, but simply put:

        PERSON_ID;GENDER;START;STOP

The rows do not contain the values "Male" or "Female", instead we use a code list found in the accompanying metadata.
In this dataset, the row contains "1" for "Male" or "2" for "Female".

        00000000000001;2;;2020-01-01
        00000000000002;1;;2020-01-01

The temporality type of this dataset is "FIXED". This means that the state of data has been recorded at a set point in time and is not subject to change. Therefore, there is no need to add a timespan to each row of data.
Still, the STOP column is required as it is used to describe when the data was recorded.
&nbsp;

&nbsp;

### SYNT_BEFOLKNING_SIVSTAND
This dataset contains synthetic data describing the marital status of a group of persons.
The structure of a row in the data is described well by the metadata, but simply put:

        PERSON_ID;STATUS;START;STOP

Similarly to SYNT_BEFOLKNING_KJOENN, the data refers to codes described further with a code list in the accompanying metadata. However, in this dataset not all codes are valid for all timespans.
If we explore the metadata file, we notice that code 6 ("Registrert partner") is not valid before 1927. During validation, rows with a timespan that starts before 1927 that refer to code 6 are considered invalid.
The temporality type of this dataset is "EVENT". A START date is therefore required. If there is no STOP date present in the row, the assumption is that the described state is ongoing.
If code 1 means "married", and code 2 means "unmarried":

        000000000000001;2;1980-01-01;1999-12-31;
        000000000000001;1;2000-01-01;;

The person(000000000000001) describe here was unmarried from January 1st, 1980 until January 1st, 2000 when they got married. The lack of a STOP date in the second row suggests that they are still married.
It is important that events for the same person do not intersect. Considering the same person:

        000000000000001;2;1980-01-01;2000-12-31;
        000000000000001;1;2000-01-01;;

The person is now described to be both married, and unmarried, for the entirety of the year 2000. This is considered invalid due to the intersection of the two timespans.
&nbsp;

&nbsp; 

