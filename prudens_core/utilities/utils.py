from typing import Dict, Any


def parse_dict_prop(
    init_dict: Dict, dict_key: str, class_name: str, **kwargs: Dict
) -> Any:
    try:
        object_attr = init_dict[dict_key]
    except KeyError:
        if "default_value" in kwargs.keys():
            object_attr = kwargs["default_value"]
        else:
            raise KeyError(
                f"Missing key '{dict_key}' in {class_name} initialization from dict."
            )
    if "expected_types" in kwargs.keys():
        if type(object_attr) not in kwargs["expected_types"]:
            types_str = ", ".join([f"'{x}'" for x in kwargs["expected_types"]])
            raise TypeError(
                f"Expected input of type {types_str} for {class_name}.{dict_key} but received {type(object_attr)}."
            )
    return object_attr
