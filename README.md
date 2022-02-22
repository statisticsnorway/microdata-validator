# microdata-validator

Python package for validating datasets in the microdata platform.


### **Dataset description**
A dataset as defined in microdata consists of one data file, and one metadata file.

The data file is a csv-file seperated by semicolons. A valid example would be:
```csv
000000000000001;123;2020-01-01;2020-12-31;
000000000000002;123;2020-01-01;2020-12-31;
000000000000003;123;2020-01-01;2020-12-31;
000000000000004;123;2020-01-01;2020-12-31;
```
Read more about the data format and columns in the [docs](/docs).

The metadata files should be in json format. The requirements for the metadata is best described through the [json schema](/microdata_validator/DatasetMetadataSchema.json), [the examples](/docs/examples), and [the documentation](/docs).

### **Usage**

Once you have your metadata and data files ready to go, they should be named and stored like this:
```
my-input-directory/
    my_dataset_name/
        my_dataset_name.csv
        my_dataset_name.json
```


Install microdata-validator through pip:
```
pip install microdata-validator
```

Import microdata-validator in your script and validate your files:
```py
from microdata_validator import validate

validation_errors = validate("my-dataset-name")

if not validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
    # You can print your errors like this:
    for error in validation_errors:
        print(error)
```


The input directory is set to the directory of the script by default.
If you wish to use a different directory, you can use the ```input_directory```-parameter:

```py
from microdata-validator import validate

validation_errors = validate(
    "my-dataset-name",
    input_directory="/my/input/directory",
)

if not validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
 ```

The validate function will temporarily generate some files in order to validate your dataset. To do this, it will create a working directory in the same location as your script. Therefore, it is important that you have writing permissions in your directory. You can also choose to define the location of this directory yourself using the ```working_directory```-parameter.

```py
from microdata-validator import validate

validation_errors = validate(
    "my-dataset-name",
    input_directory="/my/input/directory",
    working_directory="/my/working/directory"
)

if not_validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
 ```

**BE CAREFUL:**
You can set the ```delete_working_directory```-parameter to True, if you want the script to delete the generated files in the working directory after validating. These files will be lost forever.
