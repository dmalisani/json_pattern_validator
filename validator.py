import re
import json

DATA_TYPE_VALIDATOR = {
    "string": r"(.)+",
    "email": r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
    "cuit": r"(.)+",
    "ISO3166": r"^([A-Z]{0,2})$",
    "cbu": r"(.)+",
    "date": r"(.)+",
    "number": r"[-+]?[0-9]+(\.[0-9]+)?$",
}


class Evaluator():

    def __init__(self, schema, json_to_validate, autoevaluate=True):
        self.schema = schema
        self.tested = json_to_validate
        if type(schema) is str:
            self.schema = json.loads(schema)
        assert type(self.schema) is dict, "schema must be a dict or valid json"
        if type(json_to_validate) == str:
            self.tested = json.loads(json_to_validate)
        assert type(self.tested) is dict, \
            "json_to_validate must be a dict or valid json"
        self.found_errors = []
        if autoevaluate:
            self.evaluate()

    def evaluate(self):
        self._evaluate(self.schema, self.tested)

    def add_type_validator(self, name, handler):
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
        if callable(validator):
            valid = validator(data)
        else:
            pattern = re.compile(validator)
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
        try:
            for branch in schema.items():
                unpacked = self._unpack(branch)
                key = unpacked["key"]
                required = unpacked["required"]
                datatype = unpacked["datatype"]
                if required:
                    data = tested.get(key)
                    assert data, f"{key} not found"
                    if datatype is dict:
                        subbranch = branch[1]
                        try:
                            self._evaluate(subbranch, data)
                        except AssertionError as e:
                            self.found_errors.append(e.args[0])
                    else:
                        assert self._valid_data(datatype, data), \
                            f"{key} is not well formatted"
        except AssertionError as e:
            self.found_errors.append(e.args[0])

    @property
    def errors(self):
        return self.found_errors


if __name__ == "__main__":
    RPO_STRUCTURE = {
        "!version": "string",
        "!Cdtr": {
            "!CtctDtls": {
                "!EmailAdr": "email"
            },
            "!Id": {
                "!PrvtId": {
                    "!Othr": {
                        "!Id": "cuit"
                    }
                }
            },
            "!Nm": "number",
            "!PstlAdr": {
                "!BldgNb": "string",
                "!Ctry": "ISO3166",
                "PstCd": "string",
                "!StrtNm": "string",
                "!TwnNm": "string"
            }
        },
        "!CdtrAcct": {
            "!Id": {
                "!Othr": {
                    "!Id": "cbu"
                }
            }
        },
        "!Dbtr": {
            "!CtctDtls": {
                "!EmailAdr": "email"
            },
            "!Id": {
                "!PrvtId": {
                    "!Othr": {
                        "!Id": "cuit"  # TODO: ¿es internacional esto?
                    }
                }
            },
            "!Nm": "number",
            "!PstlAdr": {
                "!Ctry": "string",
                "PstCd": "string",
                "!StrtNm": "string",
                "!TwnNm": "string"
            }
        }
    }

    tested_dict = {
        #"version": "32",
        "Cdtr": {
            "CtctDtls": {
                "EmailAdr": "dn@dm.com"
            },
            "Id": {
                "PrvtId": {
                    "Othr": {
                        "Id": "333"
                    }
                }
            },
            "Nm": "3322",
            "PstlAdr": {
                "BldgNb": "aaaaaaa",
                "Ctry": "US",
                "PstCd": "cccccccc",
                "StrtNm": "ddddd",
                "TwnNm": "fffff"
            }
        },
        "CdtrAcct": {
            "Id": {
                "Othr": {
                    "Id": "3333"
                }
            }
        },
        "Dbtr": {
            "CtctDtls": {
                "EmailAdr": "ddd@gmail.com"
            },
            "Id": {
                "PrvtId": {
                    "Othr": {
                        "Id": "0099"
                    }
                }
            },
            "Nm": "3344",
            "PstlAdr": {
                "Ctry": "AR",
                "PstCd": "",
                "StrtNm": "hhhhh",
                "TwnNm": "mmm"
            }
        }
        }

    e = Evaluator(RPO_STRUCTURE, tested_dict)
    print(e.errors)
