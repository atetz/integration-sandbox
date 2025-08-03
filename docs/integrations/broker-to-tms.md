# Broker event to TMS event Integration

This document describes the mapping between the broker (visibility platform) event message and the TMS (Transport Management System) shipment event.

## Integration Notes
- Location references in broker events should match the `location.code` field from original TMS stops
- Event sequence is not strictly enforced - events may arrive out of order
- At the moment only 1 occurrence per event type allowed per shipment. A new trigger overwrites event data.
  

## Mapping table legend

| Target                   | Source      |
| ------------------------ | ----------- |
| CreateTmsShipmentEvent | BrokerEventMessage |

See bottom of page for example payloads.

## Event Metadata
| Field | Source | Notes |
|-------|--------|-------|
| created_at | situation.registrationDate | Date-time when event was registered in broker system |
| occured_at | situation.actualDate | Date-time when event actually occurred |
| source | N/A | Fixed value "broker". Identifies originating system |
|external_order_reference|order.reference|Broker order reference. 
| event_type | situation.event | See event type mapping below |

## Location Details (when applicable)
| Field | Source | Notes |
|-------|--------|-------|
| location.code | situation.position.locationReference | Location identifier from original TMS stop |
| location.latitude | situation.position.latitude | GPS latitude coordinate |
| location.longitude | situation.position.longitude | GPS longitude coordinate |

## Event Type Mapping

### Location-Based Events
| Broker Event Type | TMS Event Type | Location Source | Notes |
|-------------------|----------------|----------------|-------|
| DRIVING_TO_LOAD | DISPATCHED | Pickup location  | Driver en route to pickup |
| ORDER_LOADED | PICKED_UP | Pickup location  | Goods collected from pickup |
| ETA_EVENT | ETA_CHANGED | Delivery location  | Estimated arrival time updated |
| ORDER_DELIVERED | DELIVERED | Delivery location  | Goods delivered to consignee |

### Non-Location Events
| Broker Event Type | TMS Event Type | Location Source | Notes |
|-------------------|----------------|----------------|-------|
| ORDER_CREATED | BOOKED | N/A | Initial order booking |
| CANCEL_ORDER | CANCELLED | N/A | Order cancellation |

## Value Mappings

### Event Status Flow
| Sequence | Broker Event | TMS Event | Description |
|----------|--------------|-----------|-------------|
| 1 | ORDER_CREATED | BOOKED | Order accepted and confirmed |
| 2 | DRIVING_TO_LOAD | DISPATCHED | Driver assigned and en route |
| 3 | ORDER_LOADED | PICKED_UP | Goods loaded at pickup location |
| 4 | ETA_EVENT | ETA_CHANGED | Delivery time estimate updated |
| 5 | ORDER_DELIVERED | DELIVERED | Goods delivered successfully |
| * | CANCEL_ORDER | CANCELLED | Order cancelled (can occur anytime) |

## BrokerEventMessage example
```
{
    "id": "9c1ffc89-e730-46ee-b470-b685a1380e52",
    "shipmentId": "3f9e69bf-58c1-4216-b23e-23de0e33727a",
    "dateTransmission": "2025-07-22T18:38:22",
    "owner": "Adam's logistics",
    "order": {
      "reference": "ORD-85494",
      "eta": "2025-08-04T19:00:43.342250"
    },
    "situation": {
      "event": "DRIVING_TO_LOAD",
      "registrationDate": "2025-07-22T18:38:22",
      "actualDate": "2025-07-22T10:00:00",
      "position": {
        "locationReference": "LOC-6148",
        "latitude": 4.50606,
        "longitude": 8.833057
      }
    },
    "carrier": "Russell, Pugh and Thomas Transport"
  }
```

## CreateTmsShipmentEvent
```
{
    "created_at": "2025-07-22T18:38:22",
    "event_type": "DISPATCHED",
    "occured_at": "2025-07-22T10:00:00",
    "external_order_refere": "ORD-85494",
    "source": "broker",
    "location": {
      "code": "LOC-2813",
      "latitude": 4.50606,
      "longitude": 8.833057
    }
}
```