Validation schema based of a json string or a dict

Schema:
=======
* You must define a dict which will match with a json/dict under test
* add **!** at begin fo key for to indicate a required field
* In value of that key you will need specify a validator for such field
* That validator have to be a valid default validator or you can add your own
```
    EXAMPLE_SCHEMA = {
        "!version": "string",
        "!email": "email",
        "!data": {
            "!Id": "number",
            "title": "string"  # optional
            },
        }
 ```
 

Usage:
======
    Example:
```
    ok_json = {
        "version": "1.0.1a",
        "email": "test@test.com",
        "data": {
            "Id": 231,
            "title": "description"
        }
    }
    e = JSONEvaluator()
    e.set_schema(EXAMPLE_SCHEMA)
    e.evaluate(ok_json)
    if e.ok:
       print("Dict validate")
    else:
       print("errors found:")
       print(e.errors)
        
```
