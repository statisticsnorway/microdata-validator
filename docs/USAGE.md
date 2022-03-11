# USAGE

* Get started(/docs/USAGE.md#get-started)
* Validate dataset(/docs/USAGE.md#validate-dataset)
* Validate metadata only (/docs/USAGE.md#validate-metadata)

## Get started

Install microdata-validator through pip:
```sh
pip install microdata-validator
```

Upgrade to a newer version
```sh
pip install microdata-validator --upgrade
```

Import into your python script like so:
```py
import microdata_validator
```


## Validate dataset

Once you have your metadata and data files ready to go, they should be named and stored like this:
```
my-input-directory/
    my_dataset_name/
        my_dataset_name.csv
        my_dataset_name.json
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
from microdata_validator import validate

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
from microdata_validator import validate

validation_errors = validate(
    "my-dataset-name",
    input_directory="/my/input/directory",
    working_directory="/my/working/directory"
)

if not validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
 ```

 **BE CAREFUL:**
You can set the ```delete_working_directory```-parameter to True, if you want the script to delete the generated files in the working directory after validating. These files will be lost forever.

## Validate metadata
What if your data is not yet done, but you want to start generating and validating your metadata?
You can validate the metadata by itself with the validate_metadata-function:
```py
from microdata_validator import validate_metadata

validation_errors = validate_metadata(
    "path/to/metadata-file.json"
)

if not validation_errors:
    print("Metadata looks good")
else:
    print("Invalid metadata :(")
 ```
This will only check if all required fields are present, and that the metadata follows the correct structure. Since it does not have the data file it can not do the more complex validations. It may still be a helpful way to discover errors early.
