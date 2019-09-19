import re
import json
from validators import (
    cbu_validator,
    cuit_validator,
    great_than_validator,
)

DATA_TYPE_VALIDATOR = {
    "string": r"(.)+",
    "xstring": r"\\s+$",
    "email": r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
    "cuit": r"(.)+",
    "ISO3166": r"^([A-Z]{0,2})$",
    "cbu": r"(.)+",
    "date": r"(.)+",
    "number": r"[-+]?[0-9]+(\.[0-9]+)?$",
    "greater_than_10": great_than_validator
}


class JSONEvaluator():

    """
    This class evaluates if a given json match a pattern

    Methods:
        set_schema(schema)  -> dict or json string if wasn't provided at instance creation
        evaluate(json_for_test)

    Properties:
    ok -> if given json pass validation
    errors - > list of found errors
    """

    def __init__(self, schema=None):
        self.found_errors = []
        self._schema = None
        if schema:
            self.set_schema(schema)

    def set_schema(self, schema):
        """Loads a schema for validate json string or dicts"""
        if type(schema) is str:
            try:
                self._schema = json.loads(schema)
            except Exception:
                raise ValueError("Not valid string. Must be a Json")
        assert type(schema) is dict, "schema must be a dict or valid json"
        self._schema = schema

    def evaluate(self, json_to_validate):
        """Test if given json/dict match loaded schema"""
        assert self._schema is not None, "You have to set a schema first."
        if type(json_to_validate) == str:
            try:
                self.tested = json.loads(json_to_validate)
            except ValueError:
                raise ValueError("Not valid string. Must be a Json")
        assert type(json_to_validate) is dict, \
            "json_to_validate must be a dict or valid json"

        self._evaluate(self._schema, json_to_validate)

    def add_custom_type_validator(self, name, handler):
        """Add or overwrite validators (regex or callable)"""
        assert type(name) is str, "Name is not a string"
        assert type(handler) is str or callable(handler), \
            "handler must be a regex string or a callable"
        DATA_TYPE_VALIDATOR[name] = handler

    def _key_isrequired(self, key):
        required = key[0] == "!"
        key = key if not required else key[1:]
        return key, required

    def _valid_data(self, datatype, data):
        valid = False
        validator = DATA_TYPE_VALIDATOR.get(datatype)
        assert validator is not None
        if callable(validator):
            valid = validator(data, datatype=datatype)
        else:
            pattern = re.compile(validator)
            data = str(data) if type(data) is not str else data
            search = pattern.search(data)
            valid = search is not None
        return valid

    def _unpack(self, pattern_pair):
        pattern_key, pattern_valuetype = pattern_pair
        key, required = self._key_isrequired(pattern_key)
        pattern_valuetype = type(pattern_valuetype) if \
            type(pattern_valuetype) != str else pattern_valuetype
        return {"key": key,
                "required": required,
                "datatype": pattern_valuetype}

    def _evaluate(self, schema, tested):
        for branch in schema.items():
            try:
                unpacked = self._unpack(branch)
                key = unpacked["key"]
                required = unpacked["required"]
                datatype = unpacked["datatype"]
                data = tested.get(key)
                pressent = (data is not None) or \
                    type(data) in (str, list, dict)
                if required:
                    assert pressent, f"{key} not found"
                if datatype is dict:
                    subbranch = branch[1]
                    try:
                        self._evaluate(subbranch, data)
                    except AssertionError as e:
                        self.found_errors.append(e.args[0])
                else:
                    try:
                        valid = self._valid_data(datatype, data)
                    except AssertionError:
                        raise AssertionError(
                            f"pattern {datatype} for {key} "
                            "was not found in schema")

                    assert valid, \
                        f"{key} is not well formatted"
            except AssertionError as e:
                self.found_errors.append(e.args[0])

    @property
    def errors(self):
        """List of mandatory field that not mached"""
        return self.found_errors

    @property
    def ok(self):
        """Returns True if no errors in validation"""
        return (self._schema is not None) and (len(self.errors) == 0)

    @property
    def validators(self):
        """Return dict of current validators"""
        return DATA_TYPE_VALIDATOR



if __name__ == "__main__":
    SCHEMA_STRUCTURE = {
        "!version": "greater_than_10",
        "!email": "email",
        "!data": {
            "!subrama": {
                  "!numero": "number",
                  "!otrasubrama": {
                      "!id": "number"
                  }
                },

            "!Id": "number",
            "title": "string"  # optional
            },
        }

    ok_json = {
        "version": "2",
        "email": "test@test.com",
        "data": {
            "subrama": {
                  "numero": 18,
                  "otrasubrama": {
                      "id": 555
                  }
                },
            "Id": 231,
            "title": "description"
        }
    }
    bad_json = {
        "version": "1.0.1a",
        # "email": "test@test.com",
        "data": {
            "Id": "badtype",
            "title": "description"
        }
    }

    e = JSONEvaluator()
    e.set_schema(SCHEMA_STRUCTURE)
    e.evaluate(ok_json)
    print(e.errors)
    print(e.ok)
    # e.evaluate(bad_json)
    # print(e.errors)
    # print(e.ok)
