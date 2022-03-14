# USAGE

* Get started(/docs/USAGE.md#get-started)
* Validate dataset(/docs/USAGE.md#validate-dataset)
* Validate metadata only (/docs/USAGE.md#validate-metadata)
* Use metadata references (/docs/USAGE.md#use-metadata-references)
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


## Use metadata references
When creating metadatafiles for the microdata platform, you might find that you end up repeating yourself in each dataset.
As an example, each of the files in the [examples folder](/docs/examples) has these same attribute variables:
```json
"attributeVariables": [
    {
      "variableRole": "START_TIME",
      "shortName": "START",
      "name": [
        {"languageCode": "no", "value": "Startdato"},
        {"languageCode": "en", "value": "Start date"}
      ],
      "description": [{"languageCode": "no", "value": "Startdato/måletidspunktet for hendelsen"}
      ],
      "dataType": "DATE",
      "valueDomain": {
        "description": [{"languageCode": "no", "value": "Dato oppgitt i dager siden 1970-01-01"}]
      }
    },
    {
      "variableRole": "STOP_TIME",
      "shortName": "STOP",
      "name": [
        {"languageCode": "no", "value": "Stoppdato"},
        {"languageCode": "en", "value": "Stop date"}
      ],
      "description": [
        {"languageCode": "no", "value": "Stoppdato/sluttdato for hendelsen"},
        {"languageCode": "en", "value": "Event stop/end date"}
      ],
      "dataType": "DATE",
      "valueDomain": {
        "description": [{"languageCode": "no", "value": "Dato oppgitt i dager siden 1970-01-01"}
        ]
      }
    }
]
```
Imagine a scenario where you are managing 50+ datasets. The repetition is not only tedious, but a source of errors. Let's create a new directory ```/metadata_ref```, and place two files there:
```json
// start.json
{
    "variableRole": "START_TIME",
    "shortName": "START",
    "name": [
      {"languageCode": "no", "value": "Startdato"},
      {"languageCode": "en", "value": "Start date"}
    ],
    "description": [{"languageCode": "no", "value": "Startdato/måletidspunktet for hendelsen"}
    ],
    "dataType": "DATE",
    "valueDomain": {
    "description": [{"languageCode": "no", "value": "Dato oppgitt i dager siden 1970-01-01"}]
    }
}
```

```json
// stop.json
{
    "variableRole": "STOP_TIME",
    "shortName": "STOP",
    "name": [
      {"languageCode": "no", "value": "Stoppdato"},
      {"languageCode": "en", "value": "Stop date"}
    ],
    "description": [
      {"languageCode": "no", "value": "Stoppdato/sluttdato for hendelsen"},
      {"languageCode": "en", "value": "Event stop/end date"}
    ],
    "dataType": "DATE",
    "valueDomain": {
    "description": [{"languageCode": "no", "value": "Dato oppgitt i dager siden 1970-01-01"}
    ]
}
```

Now we can reference this "ref files" in our main dataset file:
```json
"attributeVariables": [
    {
      "$ref": "stop.json"
    },
    {
      "$ref": "start.json"
    }
]
```
By using "$ref" as the key, we can refer to a ref-file from our ref-directory. Keep in mind that we can only do this with objects, and the reference will overwrite other existing fields that may be present:
```json
"attributeVariables": [
    {
      "$ref": "stop.json",
      "otherfield": "this will be overwritten by the referenced file"
    },
    {
      "$ref": "start.json"
    }
]
```

But for the validator to know about our ref directory we need to tell it about the directory we created earlier like so:
```py
### validate example
from microdata_validator import validate

validation_errors = validate(
    "my-dataset-name",
    metadata_ref_directory="metadata_ref"    
)

### validate_metadata example
from microdata_validator import validate_metadata

validation_errors = validate_metadata(
    "path/to/metadata-file.json",
    metadata_ref_directory="metadata_ref"
)
```

**IMPORTANT!**
Remember that if you are done generating your dataset, and you want to import them into the microdata platform, we need the inlined files.
You can build an inlined file by using this function:
```py
from microdata_validator import inline_metadata

result_file_path = validate_metadata(
    "path/to/metadata-file.json",
    metadata_ref_directory="metadata_ref",
    output_file_path="path/to/inlined-metadata.json"
)
```
If you do not provide an output_file_path, the package will try to use the original path, but changing ".json" to "_inlined.json".
It will return a path object for the inlined result file.