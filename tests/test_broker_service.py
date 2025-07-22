from integrationsandbox.broker.service import validate_line_items


def test_validate_line_items_valid(
    tms_line_items,
    broker_line_items,
):
    assert validate_line_items(tms_line_items, broker_line_items) == (True, [])


def test_validate_line_items_invalid(
    tms_line_items,
    broker_line_items,
):
    broker_line_items.pop(1)
    assert False in validate_line_items(tms_line_items, broker_line_items)
