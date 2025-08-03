tms_shipment_seed_example = {
    "json_schema_extra": {
        "examples": [
            {
                "count": 10,
            }
        ]
    }
}


tms_event_example = {
    "json_schema_extra": {
        "examples": [
            {
                "id": "ae7c58f0-b476-4d9d-b958-5135b382aef2",
                "created_at": "2025-08-01T16:28:44",
                "event_type": "DISPATCHED",
                "occured_at": "2025-08-01T17:12:44",
                "external_order_reference": "ORD-85494",
                "source": "broker",
                "location": {"latitude": 4.51, "longitude": 8.83, "code": "LOC-6148"},
            }
        ]
    }
}

tms_create_event_example = {
    "json_schema_extra": {
        "examples": [
            {
                "created_at": "2025-08-01T16:28:44",
                "event_type": "DISPATCHED",
                "occured_at": "2025-08-01T17:12:44",
                "external_order_reference": "ORD-85494",
                "source": "broker",
                "location": {"latitude": 4.51, "longitude": 8.83, "code": "LOC-6148"},
            }
        ]
    }
}

tms_create_shipment_example = {
    "json_schema_extra": {
        "examples": [
            {
                "external_reference": None,
                "mode": "LTL",
                "equipment_type": "MOVING_VAN",
                "loading_meters": 15.6,
                "customer": {
                    "id": "c6593ae4-d970-413c-8fbc-9ddcff99a361",
                    "name": "Hale PLC",
                    "carrier": "Allen-Johnston Transport",
                },
                "line_items": [
                    {
                        "package_type": "BOX",
                        "stackable": True,
                        "height": 147.72,
                        "length": 70.84,
                        "width": 87.54,
                        "length_unit": "CM",
                        "package_weight": 1761.16,
                        "weight_unit": "KG",
                        "description": "Electronic gaming machines for casino installations",
                        "total_packages": 5,
                    },
                    {
                        "package_type": "BOX",
                        "stackable": True,
                        "height": 99.65,
                        "length": 107.25,
                        "width": 146.94,
                        "length_unit": "CM",
                        "package_weight": 6333.92,
                        "weight_unit": "KG",
                        "description": "Commercial grade kitchen equipment - walk-in coolers",
                        "total_packages": 3,
                    },
                    {
                        "package_type": "BOX",
                        "stackable": False,
                        "height": 30.12,
                        "length": 69.49,
                        "width": 51.45,
                        "length_unit": "CM",
                        "package_weight": 10942.95,
                        "weight_unit": "KG",
                        "description": "Bulk plastic bottles for beverage manufacturing",
                        "total_packages": 4,
                    },
                    {
                        "package_type": "BOX",
                        "stackable": True,
                        "height": 57.67,
                        "length": 166.2,
                        "width": 194.5,
                        "length_unit": "CM",
                        "package_weight": 6609.62,
                        "weight_unit": "KG",
                        "description": "Liquid fertilizer concentrate in 55-gallon drums",
                        "total_packages": 4,
                    },
                    {
                        "package_type": "PLT",
                        "stackable": True,
                        "height": 185.5,
                        "length": 95.86,
                        "width": 59.65,
                        "length_unit": "CM",
                        "package_weight": 6673.57,
                        "weight_unit": "KG",
                        "description": "Bulk cotton fabric rolls for textile manufacturing",
                        "total_packages": 2,
                    },
                ],
                "stops": [
                    {
                        "type": "PICKUP",
                        "location": {
                            "code": "LOC-3184",
                            "name": "Pieper KG",
                            "address": {
                                "address": "Adlergasse 04",
                                "city": "Miesbach",
                                "postal_code": "91204",
                                "country": "DE",
                            },
                            "latitude": 78.8133545,
                            "longitude": 86.8137,
                        },
                        "planned_date": "2025-08-06",
                        "planned_time_window_start": "06:00:00",
                        "planned_time_window_end": "17:00:00",
                    },
                    {
                        "type": "DELIVERY",
                        "location": {
                            "code": "LOC-1289",
                            "name": "Lattuada, Sagese e Parisi e figli",
                            "address": {
                                "address": "Via Flavia, 169 Piano 9",
                                "city": "Quinzanello",
                                "postal_code": "32046",
                                "country": "IT",
                            },
                            "latitude": -79.0394105,
                            "longitude": 55.347237,
                        },
                        "planned_date": "2025-08-13",
                        "planned_time_window_start": "06:00:00",
                        "planned_time_window_end": "17:00:00",
                    },
                ],
            }
        ]
    }
}


tms_shipment_example = {
    "json_schema_extra": {
        "examples": [
            {
                "id": "ef4d5f8a-0c60-4ebc-98af-bb77f61433e7",
                "external_reference": None,
                "mode": "LTL",
                "equipment_type": "MOVING_VAN",
                "loading_meters": 15.6,
                "customer": {
                    "id": "c6593ae4-d970-413c-8fbc-9ddcff99a361",
                    "name": "Hale PLC",
                    "carrier": "Allen-Johnston Transport",
                },
                "line_items": [
                    {
                        "package_type": "BOX",
                        "stackable": True,
                        "height": 147.72,
                        "length": 70.84,
                        "width": 87.54,
                        "length_unit": "CM",
                        "package_weight": 1761.16,
                        "weight_unit": "KG",
                        "description": "Electronic gaming machines for casino installations",
                        "total_packages": 5,
                    },
                    {
                        "package_type": "BOX",
                        "stackable": True,
                        "height": 99.65,
                        "length": 107.25,
                        "width": 146.94,
                        "length_unit": "CM",
                        "package_weight": 6333.92,
                        "weight_unit": "KG",
                        "description": "Commercial grade kitchen equipment - walk-in coolers",
                        "total_packages": 3,
                    },
                    {
                        "package_type": "BOX",
                        "stackable": False,
                        "height": 30.12,
                        "length": 69.49,
                        "width": 51.45,
                        "length_unit": "CM",
                        "package_weight": 10942.95,
                        "weight_unit": "KG",
                        "description": "Bulk plastic bottles for beverage manufacturing",
                        "total_packages": 4,
                    },
                    {
                        "package_type": "BOX",
                        "stackable": True,
                        "height": 57.67,
                        "length": 166.2,
                        "width": 194.5,
                        "length_unit": "CM",
                        "package_weight": 6609.62,
                        "weight_unit": "KG",
                        "description": "Liquid fertilizer concentrate in 55-gallon drums",
                        "total_packages": 4,
                    },
                    {
                        "package_type": "PLT",
                        "stackable": True,
                        "height": 185.5,
                        "length": 95.86,
                        "width": 59.65,
                        "length_unit": "CM",
                        "package_weight": 6673.57,
                        "weight_unit": "KG",
                        "description": "Bulk cotton fabric rolls for textile manufacturing",
                        "total_packages": 2,
                    },
                ],
                "stops": [
                    {
                        "type": "PICKUP",
                        "location": {
                            "code": "LOC-3184",
                            "name": "Pieper KG",
                            "address": {
                                "address": "Adlergasse 04",
                                "city": "Miesbach",
                                "postal_code": "91204",
                                "country": "DE",
                            },
                            "latitude": 78.8133545,
                            "longitude": 86.8137,
                        },
                        "planned_date": "2025-08-06",
                        "planned_time_window_start": "06:00:00",
                        "planned_time_window_end": "17:00:00",
                    },
                    {
                        "type": "DELIVERY",
                        "location": {
                            "code": "LOC-1289",
                            "name": "Lattuada, Sagese e Parisi e figli",
                            "address": {
                                "address": "Via Flavia, 169 Piano 9",
                                "city": "Quinzanello",
                                "postal_code": "32046",
                                "country": "IT",
                            },
                            "latitude": -79.0394105,
                            "longitude": 55.347237,
                        },
                        "planned_date": "2025-08-13",
                        "planned_time_window_start": "06:00:00",
                        "planned_time_window_end": "17:00:00",
                    },
                ],
                "timeline_events": None,
            }
        ]
    }
}
