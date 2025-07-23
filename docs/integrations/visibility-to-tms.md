# Visibility Platform to TMS Integration

This document describes the mapping between the broker (visibility platform) event message and the TMS (Transport Management System) shipment event.

## Integration Notes
- Location references in broker events should match the `location.code` field from original TMS stops
- Event sequence is not strictly enforced - events may arrive out of order
- At the moment only 1 occurrence per event type allowed per shipment. A new trigger overwrites event data.

## Event Metadata
| Field | Source | Notes |
|-------|--------|-------|
| created_at | situation.registrationDate | Date-time when event was registered in broker system |
| occured_at | situation.actualDate | Date-time when event actually occurred |
| source | N/A | Fixed value "broker" - identifies originating system |
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


