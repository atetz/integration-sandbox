from datetime import datetime
from typing import Any, Dict, List, Tuple

from deepdiff import DeepDiff


def serialize_value(value):
    # Normalizes data structures for deep comparison by converting Pydantic models to dicts
    if hasattr(value, "model_dump"):
        return value.model_dump()
    elif isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat()
    elif isinstance(value, float):
        return round(value, 2)
    elif isinstance(value, set):
        return list(value)
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    return value


def compare_mappings(
    tms_data: Dict[str, Any], broker_data: Dict[str, Any]
) -> Tuple[bool, List[str | None]]:
    errors = []
    all_keys = set(tms_data.keys()) | set(broker_data.keys())

    for key in all_keys:
        if key not in tms_data:
            errors.append({"field": key, "error": "missing in tms_data"})
        elif key not in broker_data:
            errors.append({"field": key, "error": "missing in broker_data"})
        else:
            tms_serialized = serialize_value(tms_data[key])
            broker_serialized = serialize_value(broker_data[key])

            diff = DeepDiff(
                tms_serialized, broker_serialized, ignore_order=True, verbose_level=1
            )

            if diff:
                errors.append(
                    {
                        "field": key,
                        "differences": diff.to_dict(),
                        "expected": tms_serialized,
                        "actual": broker_serialized,
                    }
                )

    return len(errors) == 0, errors
