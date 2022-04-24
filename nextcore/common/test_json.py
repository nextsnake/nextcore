from nextcore.common import json_loads, json_dumps

def test_loads():
    assert json_loads('{"a": 1}') == {"a": 1}


def test_dumps():
    assert json_dumps({"a": 1}) in ['{"a":1}', '{"a": 1}']


