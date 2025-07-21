# TMS to Visibility Platform Integration

This document describes the mapping between the TMS (Transport Management System) order and the Visibility Platform shipment message.

## Message Metadata
| Field | Source | Notes |
|-------|--------|-------|
| meta.senderId | N/A | Fixed value, id of organization |
| meta.messageDate | N/A | Date-time of transmission |
| meta.messageReference | id | Unique generated ref for message |
| meta.messageFunction | N/A | 9=NEW, 4=UPDATE, 1=CANCEL |

## Shipment Details
| Field | Source | Notes |
|-------|--------|-------|
| shipment.reference | id | ShipmentId of TMS |
| shipment.carrier | customer.carrier | |
| shipment.transportMode | mode | Fixed value "road" |

## Order Details
| Field | Source | Notes |
|-------|--------|-------|
| shipment.orders[].reference | id | ShipmentId of TMS since the TMS shipment only has 1 order |
| shipment.orders[].goodsDescription | line_items[].description | Concatenated from all line items with a pipe separator '\|' |
| shipment.orders[].quantity.grossWeight | line_items[].package_weight + total_packages | Sum of (weight × quantity) |
| shipment.orders[].quantity.loadingMeters | loading_meters ||

## Pickup Location
| Field | Source | Notes |
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
| Field | Source | Notes |
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
| Field | Source | Notes |
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

