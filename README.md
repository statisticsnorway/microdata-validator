# microdata-validator

Python package for validating datasets in the microdata platform.


### **Dataset description**
A dataset as defined in microdata consists of one data file, and one metadata file.

The data file is a csv file seperated by semicolons. A valid example would be:
```csv
000000000000001;123;2020-01-01;2020-12-31;
000000000000002;123;2020-01-01;2020-12-31;
000000000000003;123;2020-01-01;2020-12-31;
000000000000004;123;2020-01-01;2020-12-31;
```
Read more about the data format and columns in [the documentation](/docs).

The metadata files should be in json format. The requirements for the metadata is best described through the [json schema](/microdata_validator/schema/dataset_metadata_schema.json), [the examples](/docs/examples), and [the documentation](/docs).

### **Basic usage**

Once you have your metadata and data files ready to go, they should be named and stored like this:
```
my-input-directory/
    MY_DATASET_NAME/
        MY_DATASET_NAME.csv
        MY_DATASET_NAME.json
```
Note that the filename only allows upper case letters A-Z, number 0-9 and underscores.


Then use pip to install microdata-validator:
```
pip install microdata-validator
```

Import microdata-validator in your script and validate your files:
```py
from microdata_validator import validate

validation_errors = validate(
    "MY_DATASET_NAME",
    input_directory="path/to/my-input-directory"
)

if not validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
    # You can print your errors like this:
    for error in validation_errors:
        print(error)
```

 For a more in-depth explanation of usage visit [the usage documentation](/docs/USAGE.md).

