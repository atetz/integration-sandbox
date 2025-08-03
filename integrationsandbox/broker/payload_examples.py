create_broker_order = {
    "json_schema_extra": {
        "examples": [
            {
                "meta": {
                    "senderId": "75831ed4-7d29-44a6-953f-066c2e3cd609",
                    "messageDate": "2025-07-20T11:35:47.461Z",
                    "messageReference": "976eb041-b766-4286-a378-0938c65e7050",
                    "messageFunction": 9,
                },
                "shipment": {
                    "reference": "976eb041-b766-4286-a378-0938c65e7050",
                    "carrier": "Cole Ltd Transport",
                    "transportMode": "ROAD",
                    "orders": [
                        {
                            "reference": "976eb041-b766-4286-a378-0938c65e7050",
                            "pickUp": {
                                "identification": "LOC-9973",
                                "name": "Scamarcio e figli",
                                "address1": "Borgo Buonauro, 27 Piano 6",
                                "address2": "",
                                "country": "IT",
                                "postalCode": "81046",
                                "city": "Riva",
                                "latitude": 9.223782,
                                "longitude": 123.12346,
                                "instructions": "",
                                "dates": [
                                    {
                                        "qualifier": "PERIOD_EARLIEST",
                                        "dateTime": "2025-07-22T06:00:00Z",
                                    },
                                    {
                                        "qualifier": "PERIOD_LATEST",
                                        "dateTime": "2025-07-22T17:00:00Z",
                                    },
                                ],
                            },
                            "consignee": {
                                "identification": "LOC-8521",
                                "name": "Williams-Patel",
                                "address1": "Studio 6 Gill courts",
                                "address2": "",
                                "country": "GB",
                                "postalCode": "WA7 6JT",
                                "city": "Leonardtown",
                                "latitude": 13.042235,
                                "longitude": -168.601537,
                                "instructions": "",
                                "dates": [
                                    {
                                        "qualifier": "PERIOD_EARLIEST",
                                        "dateTime": "2025-07-24T06:00:00Z",
                                    },
                                    {
                                        "qualifier": "PERIOD_LATEST",
                                        "dateTime": "2025-07-24T17:00:00Z",
                                    },
                                ],
                            },
                            "goodsDescription": "Commercial grade floor mats for high-traffic areas, Heavy-duty truck tires, new and retreaded options, Industrial conveyor belt sections",
                            "quantity": {
                                "grossWeight": 30605.77,
                                "loadingMeters": 14.8,
                            },
                            "handlingUnits": [
                                {
                                    "packagingQualifier": "BL",
                                    "grossWeight": 7069.62,
                                    "width": 20.88,
                                    "length": 138.51,
                                    "height": 115.15,
                                },
                                {
                                    "packagingQualifier": "BL",
                                    "grossWeight": 7069.62,
                                    "width": 20.88,
                                    "length": 138.51,
                                    "height": 115.15,
                                },
                                {
                                    "packagingQualifier": "BL",
                                    "grossWeight": 7069.62,
                                    "width": 20.88,
                                    "length": 138.51,
                                    "height": 115.15,
                                },
                                {
                                    "packagingQualifier": "BL",
                                    "grossWeight": 7069.62,
                                    "width": 20.88,
                                    "length": 138.51,
                                    "height": 115.15,
                                },
                                {
                                    "packagingQualifier": "CY",
                                    "grossWeight": 2336.24,
                                    "width": 162.91,
                                    "length": 71.51,
                                    "height": 31.16,
                                },
                                {
                                    "packagingQualifier": "CY",
                                    "grossWeight": 890.43,
                                    "width": 95.14,
                                    "length": 111.34,
                                    "height": 66.97,
                                },
                                {
                                    "packagingQualifier": "CY",
                                    "grossWeight": 890.43,
                                    "width": 95.14,
                                    "length": 111.34,
                                    "height": 66.97,
                                },
                                {
                                    "packagingQualifier": "CY",
                                    "grossWeight": 890.43,
                                    "width": 95.14,
                                    "length": 111.34,
                                    "height": 66.97,
                                },
                            ],
                        }
                    ],
                },
            }
        ]
    },
}


create_broker_event = {
    "json_schema_extra": {
        "examples": [
            {
                "id": "9c1ffc89-e730-46ee-b470-b685a1380e52",
                "shipmentId": "3f9e69bf-58c1-4216-b23e-23de0e33727a",
                "dateTransmission": "2025-08-01T16:18:53.279401",
                "owner": "Adam's logistics",
                "order": {
                    "reference": "ORD-85494",
                    "eta": "2025-08-04T19:00:43.342250",
                },
                "situation": {
                    "event": "DRIVING_TO_LOAD",
                    "registrationDate": "2025-08-01T16:28:44.637944",
                    "actualDate": "2025-08-01T17:12:44.637944",
                    "position": {
                        "locationReference": "LOC-6148",
                        "latitude": 4.50606,
                        "longitude": 8.833057,
                    },
                },
                "carrier": "Russell, Pugh and Thomas Transport",
            }
        ]
    }
}

broker_event = {
    "json_schema_extra": {
        "examples": [
            {
                "id": "9c1ffc89-e730-46ee-b470-b685a1380e52",
                "shipmentId": "3f9e69bf-58c1-4216-b23e-23de0e33727a",
                "dateTransmission": "2025-08-01T16:18:53.279401",
                "owner": "Adam's logistics",
                "order": {
                    "reference": "ORD-85494",
                    "eta": "2025-08-04T19:00:43.342250",
                },
                "situation": {
                    "event": "DRIVING_TO_LOAD",
                    "registrationDate": "2025-08-01T16:28:44.637944",
                    "actualDate": "2025-08-01T17:12:44.637944",
                    "position": {
                        "locationReference": "LOC-6148",
                        "latitude": 4.50606,
                        "longitude": 8.833057,
                    },
                },
                "carrier": "Russell, Pugh and Thomas Transport",
            }
        ]
    }
}

broker_event_seed = {
    "json_schema_extra": {
        "examples": [
            {
                "event": "DRIVING_TO_LOAD",
                "shipment_ids": ["3f9e69bf-58c1-4216-b23e-23de0e33727a"],
            }
        ]
    }
}
