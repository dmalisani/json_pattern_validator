import pytest
from json_pattern_validator import JSONEvaluator

BASE_SCHEMA = {
    "!version": "number",
    "!email": "email",
    "!data": {
        "!childbranch": {
                "!price": "number",
                "!subchildbranch": {
                    "!id": "number"
                }
            },

        "!Id": "number",
        "title": "string"  # optional
        },
}



def test_instantiate_no_schema_ok():
    js = JSONEvaluator()
    assert isinstance(js, JSONEvaluator)

def test_instantiate_with_schema_ok():
    js = JSONEvaluator(BASE_SCHEMA)
    assert isinstance(js, JSONEvaluator)
    assert js.ok
    assert js.errors == []

def test_instantiate_with_bad_schema_ok():
    with pytest.raises(ValueError):
        js = JSONEvaluator("bad_json")

def test_evaluate_ok_with_optional():
    ok_json = {
        "version": "2",
        "email": "test@test.com",
        "data": {
            "childbranch": {
                  "price": 18,
                  "subchildbranch": {
                      "id": 555
                  }
                },
            "Id": 231,
            "title": "description"
        }
    }
    js = JSONEvaluator(BASE_SCHEMA)
    js.evaluate(ok_json)
    assert js.errors == []
    assert js.ok

def test_evaluate_ok_no_optional():
    ok_json = {
        "version": "2",
        "email": "test@test.com",
        "data": {
            "childbranch": {
                  "price": 18,
                  "subchildbranch": {
                      "id": 555
                  }
                },
            "Id": 231,
        }
    }
    js = JSONEvaluator(BASE_SCHEMA)
    js.evaluate(ok_json)
    assert js.errors == []
    assert js.ok    

PARAMETRIZED_TEST = [
    ({"!only_number": "number"}, {"only_number": 23}, True, []),
    ({"!only_number": "number"}, {"only_number": "23"}, True, []),
    ({"opt_number": "number", "!text": "string"}, {"opt_number": "23", "text": "text"}, True, []),
    ({"!numeric": "number", "!text": "string"}, {"text": "text"}, False, ["[]: numeric not found"]),
    ({"!numeric": "number", "!text": "string"}, {"numeric": 34}, False, ["[]: text not found"]),
    ({"!numeric": "number", "opt_text": "string"}, {"numeric": "23"}, True, []),
    ({"!numeric": "number"}, {"numeric": "not_valid"}, False, ["[]: numeric is not well formatted"]),
    ({"!root": {"!numeric": "number"}}, {"root": {"numeric": 2}}, True, []),
    ({"!root": {"!numeric": "number"}}, {"root": {"numeric": "2"}}, True, []),
    ({"!root": {"!numeric": "number"}}, {"root": {"numeric": "xx"}}, False, ["[root]: numeric is not well formatted"]),
    ({"!root": {"!numeric": "number", "opt_text":"string"}}, {"root": {"numeric": 2, "opt_text":"sometext"}}, True, []),
    ({"!root": {"!numeric": "number", "opt_text":"string"}}, {"root": {"numeric": 2}}, True, []),    
]
@pytest.mark.parametrize("schema,input_data,ok,error", PARAMETRIZED_TEST)
def test_multiple(schema, input_data, ok, error):
    js = JSONEvaluator(schema)
    js.evaluate(input_data)
    assert js.errors == error
    assert js.ok == ok 


def test_evaluate_debug_1():
    ok_json = {
        "version": "2",
        "email": "test@test.com",
        "data": {
            "childbranch": {
                  "price": 18,
                  "subchildbranch": {
                      "id": 555
                  }
                },
            "Id": 231,
        }
    }
    js = JSONEvaluator(BASE_SCHEMA, debug=True)
    js.evaluate(ok_json)
    assert js.errors == []
    assert js.ok
