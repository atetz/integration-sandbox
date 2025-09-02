# TMS Shipment to Broker Order Integration

This document describes the mapping between the TMS (Transport Management System) order and the Visibility Platform shipment message.


## Mapping table legend

| Target | Source |
| ------- | -------- |
| CreateBrokerOrderMessage | TmsShipment |

See bottom of page for example payloads.


## Message Metadata
| Target | Source | Notes |
|-------|--------|-------|
| meta.senderId | N/A | Fixed value, id of organization |
| meta.messageDate | N/A | Date-time of transmission |
| meta.messageReference | id | Unique generated ref for message |
| meta.messageFunction | N/A | 9=NEW, 4=UPDATE, 1=CANCEL |

## Shipment Details
| Target | Source | Notes |
|-------|--------|-------|
| shipment.reference | id | ShipmentId of TMS |
| shipment.carrier | customer.carrier | |
| shipment.transportMode | mode | Fixed value "road" |

## Order Details
| Target | Source | Notes |
|-------|--------|-------|
| shipment.orders[].reference | id | ShipmentId of TMS since the TMS shipment only has 1 order |
| shipment.orders[].goodsDescription | line_items[].description | Concatenated from all line items with a pipe separator '\|' |
| shipment.orders[].quantity.grossWeight | line_items[].package_weight * total_packages | Sum of (weight × quantity) |
| shipment.orders[].quantity.loadingMeters | loading_meters ||

## Pickup Location
| Target | Source | Notes |
|-------|--------|-------|
| shipment.orders[].pickUp.identification | stops[type=PICKUP].location.code | |
| shipment.orders[].pickUp.name | stops[type=PICKUP].location.name | |
| shipment.orders[].pickUp.address1 | stops[type=PICKUP].location.address.address | |
| shipment.orders[].pickUp.address2 | N/A | |
| shipment.orders[].pickUp.country | stops[type=PICKUP].location.address.country | |
| shipment.orders[].pickUp.postalCode | stops[type=PICKUP].location.address.postal_code | |
| shipment.orders[].pickUp.city | stops[type=PICKUP].location.address.city | |
| shipment.orders[].pickUp.latitude | stops[type=PICKUP].location.latitude | |
| shipment.orders[].pickUp.longitude | stops[type=PICKUP].location.longitude | |
| shipment.orders[].pickUp.instructions | N/A | |
| shipment.orders[].pickUp.dates[].qualifier | PERIOD_EARLIEST or PERIOD_LATEST | Based on start or end of time window|
| shipment.orders[].pickUp.dates[].dateTime | stops[type=PICKUP].planned_date + planned_time_window_start or stops[type=PICKUP].planned_date + planned_time_window_end | |

## Delivery Location
| Target | Source | Notes |
|-------|--------|-------|
| shipment.orders[].consignee.identification | stops[type=DELIVERY].location.code | |
| shipment.orders[].consignee.name | stops[type=DELIVERY].location.name | |
| shipment.orders[].consignee.address1 | stops[type=DELIVERY].location.address.address | |
| shipment.orders[].consignee.address2 | N/A | |
| shipment.orders[].consignee.country | stops[type=DELIVERY].location.address.country | |
| shipment.orders[].consignee.postalCode | stops[type=DELIVERY].location.address.postal_code | |
| shipment.orders[].consignee.city | stops[type=DELIVERY].location.address.city | |
| shipment.orders[].consignee.latitude | stops[type=DELIVERY].location.latitude | |
| shipment.orders[].consignee.longitude | stops[type=DELIVERY].location.longitude | |
| shipment.orders[].consignee.instructions | N/A | |
| shipment.orders[].consignee.dates[].qualifier | PERIOD_EARLIEST or PERIOD_LATEST | Based on start or end of time window|
| shipment.orders[].consignee.dates[].dateTime | stops[type=DELIVERY].planned_date + planned_time_window_start or stops[type=DELIVERY].planned_date + planned_time_window_end | |

## Handling Units
**Note: handlingUnits[] is a repeating data structure mapping per line_items[].total_packages.**

| Target | Source | Notes |
|-------|--------|-------|
| shipment.orders[].handlingUnits[].packagingQualifier | line_items[].package_type | See package mapping below |
| shipment.orders[].handlingUnits[].grossWeight | line_items[].package_weight | Weight per unit |
| shipment.orders[].handlingUnits[].width | line_items[].width | Direct mapping in CM |
| shipment.orders[].handlingUnits[].length | line_items[].length | Direct mapping in CM |
| shipment.orders[].handlingUnits[].height | line_items[].height | Direct mapping in CM |

## Value Mappings

### Message Function Mapping
| Value | Description |
|-------|-------------|
| 9 | NEW order |
| 4 | UPDATE existing order |
| 1 | CANCEL order |

### Time Window Mapping
| TMS Time Window | Broker Date Qualifier |
|----------------|---------------------|
| planned_time_window_start | PERIOD_EARLIEST |
| planned_time_window_end | PERIOD_LATEST |

### Package Type Mapping
| TMS Package Type | Broker Packaging Qualifier | Description |
|-----------------|--------------------------|-------------|
| BALE | BL | Baled goods |
| BOX | BX | Boxed items |
| COIL | CL | Coiled materials |
| CYLINDER | CY | Cylindrical containers |
| DRUM | DR | Drum containers |
| OTHER | OT | Other package types |
| PLT | PL | Palletized goods |
| CRATE | BX | Crated items (mapped to box) |


## TmsShipment Example
```
{
  "id": "67f055d4-25fe-47ef-a7cf-4c369c406a05",
  "external_reference": null,
  "mode": "LTL",
  "equipment_type": "MOVING_VAN",
  "loading_meters": 14.8,
  "customer": {
    "id": "75831ed4-7d29-44a6-953f-066c2e3cd609",
    "name": "Clark-Acosta",
    "carrier": "Cole Ltd Transport"
  },
  "line_items": [
    {
      "package_type": "BALE",
      "stackable": false,
      "height": 115.15,
      "length": 138.51,
      "width": 20.88,
      "length_unit": "CM",
      "package_weight": 7069.62,
      "weight_unit": "KG",
      "description": "Commercial grade floor mats for high-traffic areas",
      "total_packages": 4
    },
    {
      "package_type": "CYLINDER",
      "stackable": true,
      "height": 31.16,
      "length": 71.51,
      "width": 162.91,
      "length_unit": "CM",
      "package_weight": 2336.24,
      "weight_unit": "KG",
      "description": "Heavy-duty truck tires, new and retreaded options",
      "total_packages": 1
    },
    {
      "package_type": "CYLINDER",
      "stackable": false,
      "height": 66.97,
      "length": 111.34,
      "width": 95.14,
      "length_unit": "CM",
      "package_weight": 890.43,
      "weight_unit": "KG",
      "description": "Industrial conveyor belt sections",
      "total_packages": 3
    }
  ],
  "stops": [
    {
      "type": "PICKUP",
      "location": {
        "code": "LOC-9973",
        "name": "Scamarcio e figli",
        "address": {
          "address": "Borgo Buonauro, 27 Piano 6",
          "city": "Riva",
          "postal_code": "81046",
          "country": "IT"
        },
        "latitude": 9.223782,
        "longitude": 123.12346
      },
      "planned_date": "2025-07-22",
      "planned_time_window_start": "06:00:00",
      "planned_time_window_end": "17:00:00"
    },
    {
      "type": "DELIVERY",
      "location": {
        "code": "LOC-8521",
        "name": "Williams-Patel",
        "address": {
          "address": "Studio 6\nGill courts",
          "city": "Leonardtown",
          "postal_code": "WA7 6JT",
          "country": "GB"
        },
        "latitude": 13.042235,
        "longitude": -168.601537
      },
      "planned_date": "2025-07-24",
      "planned_time_window_start": "06:00:00",
      "planned_time_window_end": "17:00:00"
    }
  ],
  "timeline_events": null
}
```

## CreateBrokerOrderMessage Example
```
{
  "meta": {
    "senderId": "75831ed4-7d29-44a6-953f-066c2e3cd609",
    "messageDate": "2025-07-20T11:35:47.461Z",
    "messageReference": "67f055d4-25fe-47ef-a7cf-4c369c406a05",
    "messageFunction": 9
  },
  "shipment": {
    "reference": "67f055d4-25fe-47ef-a7cf-4c369c406a05",
    "carrier": "Cole Ltd Transport",
    "transportMode": "ROAD",
    "orders": [
      {
        "reference": "67f055d4-25fe-47ef-a7cf-4c369c406a05",
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
              "dateTime": "2025-07-22T06:00:00Z"
            },
            {
              "qualifier": "PERIOD_LATEST",
              "dateTime": "2025-07-22T17:00:00Z"
            }
          ]
        },
        "consignee": {
          "identification": "LOC-8521",
          "name": "Williams-Patel",
          "address1": "Studio 6\nGill courts",
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
              "dateTime": "2025-07-24T06:00:00Z"
            },
            {
              "qualifier": "PERIOD_LATEST",
              "dateTime": "2025-07-24T17:00:00Z"
            }
          ]
        },
                "goodsDescription": "Industrial conveyor belt sections|Heavy-duty truck tires, new and retreaded options|Commercial grade floor mats for high-traffic areas",

        "quantity": {
          "grossWeight": 33286.01,
          "loadingMeters": 14.8
        },
        "handlingUnits": [
          {
            "packagingQualifier": "BL",
            "grossWeight": 7069.62,
            "width": 20.88,
            "length": 138.51,
            "height": 115.15
          },
          {
            "packagingQualifier": "BL",
            "grossWeight": 7069.62,
            "width": 20.88,
            "length": 138.51,
            "height": 115.15
          },
          {
            "packagingQualifier": "BL",
            "grossWeight": 7069.62,
            "width": 20.88,
            "length": 138.51,
            "height": 115.15
          },
          {
            "packagingQualifier": "BL",
            "grossWeight": 7069.62,
            "width": 20.88,
            "length": 138.51,
            "height": 115.15
          },
          {
            "packagingQualifier": "CY",
            "grossWeight": 2336.24,
            "width": 162.91,
            "length": 71.51,
            "height": 31.16
          },
          {
            "packagingQualifier": "CY",
            "grossWeight": 890.43,
            "width": 95.14,
            "length": 111.34,
            "height": 66.97
          },
          {
            "packagingQualifier": "CY",
            "grossWeight": 890.43,
            "width": 95.14,
            "length": 111.34,
            "height": 66.97
          },
          {
            "packagingQualifier": "CY",
            "grossWeight": 890.43,
            "width": 95.14,
            "length": 111.34,
            "height": 66.97
          }
        ]
      }
    ]
  }
}

```