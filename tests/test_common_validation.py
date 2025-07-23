from integrationsandbox.broker.models import BrokerQuantity
from integrationsandbox.common.validation import compare_mappings, serialize_value


def test_serialize_value_with_model():
    quantity = BrokerQuantity(loadingMeters=10.0, grossWeight=25.0)
    result = serialize_value(quantity)
    assert result == {"loadingMeters": 10.0, "grossWeight": 25.0}


def test_serialize_value_with_set():
    test_set = {"item1", "item2"}
    result = serialize_value(test_set)
    assert isinstance(result, list)
    assert set(result) == test_set


def test_serialize_value_with_list():
    quantity = BrokerQuantity(loadingMeters=5.0, grossWeight=10.0)
    test_list = [quantity, "string"]
    result = serialize_value(test_list)
    assert len(result) == 2
    assert result[0] == {"loadingMeters": 5.0, "grossWeight": 10.0}
    assert result[1] == "string"


def test_serialize_value_primitive():
    assert serialize_value("string") == "string"
    assert serialize_value(42) == 42


def test_compare_mappings_equal():
    data1 = {"field1": "value1", "field2": 42}
    data2 = {"field1": "value1", "field2": 42}

    is_valid, errors = compare_mappings(data1, data2)

    assert is_valid is True
    assert errors == []


def test_compare_mappings_different_values():
    data1 = {"field1": "value1"}
    data2 = {"field1": "value2"}

    is_valid, errors = compare_mappings(data1, data2)

    assert is_valid is False
    assert len(errors) == 1
    assert errors[0]["field"] == "field1"
    assert "differences" in errors[0]


def test_compare_mappings_missing_field_in_broker():
    data1 = {"field1": "value1", "field2": "value2"}
    data2 = {"field1": "value1"}

    is_valid, errors = compare_mappings(data1, data2)

    assert is_valid is False
    assert len(errors) == 1
    assert errors[0]["field"] == "field2"
    assert errors[0]["error"] == "missing in broker_data"


def test_compare_mappings_missing_field_in_tms():
    data1 = {"field1": "value1"}
    data2 = {"field1": "value1", "field2": "value2"}

    is_valid, errors = compare_mappings(data1, data2)

    assert is_valid is False
    assert len(errors) == 1
    assert errors[0]["field"] == "field2"
    assert errors[0]["error"] == "missing in tms_data"
    assert errors[0]["error"] == "missing in tms_data"
