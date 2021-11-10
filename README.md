# microdata-validator

Python package for validating datasets in the microdata platform.


## Usage
Install microdata-validator through pip:
```
pip install microdata-validator
```

Import microdata-validator in your script and validate your files:
```py
from microdata_validator import validate

dataset_is_valid = validate("my-dataset-name"):

if dataset_is_valid:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
```

If your dataset is valid the validate function it will return True, if not it will return False.
The error logs will be logged as you run the validation function. If you want these error logs printed to a file, you can request that throught the ´´´print_errors_to_file```-parameter:

```py
from microdata_validator import validate


dataset_is_valid = validate(
    "my-dataset-name",
    print_errors_to_file="my/error/file.log"
)

if dataset_is_valid:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
```

The default directory the script looks for files is your relative python path. If you wish to use a different directory, you can use the ```working_directory```-parameter:

```py
from microdata-validator import validate

dataset_is_valid = validate(
    "my-dataset-name",
    working_directory="/my/working/directory",
    print_errors_to_file="my/error/file.log"
)

if dataset_is_valid:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
 ```

The validate function will temporarily generate a sqlite-file to faster sort through the data in your CSV. It will clean up after itself after it is done using it, but it is important that you have write permissions to your working directory.