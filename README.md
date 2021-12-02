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

validation_errors = validate("my-dataset-name")

if not validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
    # You can print your errors like this:
    for error in validation_errors:
        print(error)
```

If your dataset is valid the validate function will return an empty error list, if not it will populate that list with the errors.
If you want these errors printed to a file, you can request that throught the ´´´print_errors_to_file```-parameter:

```py
from microdata_validator import validate


validation_errors = validate(
    "my-dataset-name",
    print_errors_to_file="my/error/file.log"
)

if not validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
```

The default directory the script looks for files is the directory from which you are running your script.
If you wish to use a different directory, you can use the ```input_directory```-parameter:

```py
from microdata-validator import validate

validation_errors = validate(
    "my-dataset-name",
    input_directory="/my/input/directory",
    print_errors_to_file="my/error/file.log"
)

if not validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
 ```

The validate function will temporarily generate some files in order to validate your dataset. It will clean up after itself when it is done, but it is important that you have write permissions to your working directory. The working directory will be created by default under your input directory, but you can define this yourself using the ```working_directory```-parameter.
If you want these files to not get deleted after validation, you can use the ```keep_generated_files```-parameter:

```py
from microdata-validator import validate

validation_errors = validate(
    "my-dataset-name",
    input_directory="/my/input/directory",
    working_directory="/my/working/directory",
    keep_generated_files=True,
    print_errors_to_file="my/error/file.log"
)

if not_validation_errors:
    print("My dataset is valid")
else:
    print("Dataset is invalid :(")
 ```
