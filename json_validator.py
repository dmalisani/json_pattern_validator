import re
import json
from validators import (
    cbu_validator,
    cuit_validator,
    date_validator,
    greater_than_validator,
)

DATA_TYPE_VALIDATOR = {
    "string": r"(.)+",
    "xstring": r"\\s+$",
    "email": r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
    "cuit": r"(.)+",
    "ISO3166": r"^([A-Z]{0,2})$",
    "cbu": cbu_validator,
    "date": date_validator,
    "cuit": cuit_validator,
    "number": r"[-+]?[0-9]+(\.[0-9]+)?$",
    "greater_than_10": greater_than_validator
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

    def __init__(self, schema=None, debug=False):
        self.found_errors = []
        self._schema = None
        if schema:
            self.set_schema(schema)
        self.debug = debug

    def set_schema(self, schema):
        """Loads a schema for validate json string or dicts"""
        if type(schema) is str:
            try:
                self._schema = json.loads(schema)
            except Exception:
                raise ValueError("Not valid string. Must be a Json")
        assert type(schema) is dict, "schema must be a dict or valid json"
        self._schema = schema

    def evaluate(self, json_to_validate, *, enable_debug=False):
        """Test if given json/dict match loaded schema"""
        assert self._schema is not None, "You have to set a schema first."
        before_debug = self.debug
        self.debug = self.debug or enable_debug
        if type(json_to_validate) == str:
            try:
                self.tested = json.loads(json_to_validate)
            except ValueError:
                raise ValueError("Not valid string. Must be a Json")
        assert type(json_to_validate) is dict, \
            "json_to_validate must be a dict or valid json"

        self._evaluate(self._schema, json_to_validate)
        self.debug = before_debug
        

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

    def _debug_print(self, *args):
        if self.debug:
            print(args)

    def _evaluate(self, schema, tested, path=None, level=0):
        for branch in schema.items():
            try:
                unpacked = self._unpack(branch)
                key = unpacked["key"]
                required = unpacked["required"]
                datatype = unpacked["datatype"]
                data = tested.get(key)
                pressent = (data is not None) or \
                    type(data) in (str, list, dict)
                path_str = path + "." if path else ""
                path_str = path_str[1:] if path_str and path_str[0] == "." else path_str
                path_str = path_str[:-1] if path_str and path_str[-1] == "." else path_str
                self._debug_print("Evaluating: {}".format(path_str))

                if required:
                    assert pressent, f"[{path_str}]: {key} not found"
                if datatype is dict:
                    subbranch = branch[1]
                    if path is not None:
                        path += "." + key
                    else:
                        path = key
                    try:
                        level += 1
                        self._evaluate(subbranch, data, path, level)
                        level -= 1
                        path = ".".join(path.split(".")[:-1])
                    except AssertionError as e:
                        self._debug_print("ERROR: {}".format(e.args[0]))
                        self.found_errors.append(e.args[0])
                else:
                    try:
                        valid = self._valid_data(datatype, data)
                    except AssertionError:
                        self._debug_print("ERROR: [{0}]: {1} pattern {2} or "
                                  "was not found in schema".format(path_str, key, datatype))
                        raise AssertionError(
                            f"[{path_str}]: {key} pattern {datatype} or "
                            "was not found in schema")
                    assert valid, \
                        f"[{path_str}]: {key} is not well formatted"
            except AssertionError as e:
                self._debug_print("ERROR: {}".format(e.args[0]))                
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
    
