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
| shipment.orders[].goodsDescription | line_items[].description | Concatenated from all line items |
| shipment.orders[].quantity.grossWeight | line_items[].package_weight + total_packages | Sum of (weight × quantity) |
| shipment.orders[].quantity.loadingMeters | line_items[] | Calculated from dimensions |

## Pickup Location
| Field | Source | Notes |
|-------|--------|-------|
| shipment.orders[].pickUp.identification | location.code | |
| shipment.orders[].pickUp.name | location.name | |
| shipment.orders[].pickUp.address1 | location.address.address | |
| shipment.orders[].pickUp.address2 | N/A | |
| shipment.orders[].pickUp.country | location.address.country | |
| shipment.orders[].pickUp.postalCode | location.address.postal_code | |
| shipment.orders[].pickUp.city | location.address.city | |
| shipment.orders[].pickUp.latitude | location.latitude | |
| shipment.orders[].pickUp.longitude | location.longitude | |
| shipment.orders[].pickUp.instructions | N/A | |
| shipment.orders[].pickUp.dates[].qualifier | N/A | Fixed value "PLANNED" |
| shipment.orders[].pickUp.dates[].dateTime | stops[type=PICKUP].planned_date + planned_time_window_start | |

## Delivery Location
| Field | Source | Notes |
|-------|--------|-------|
| shipment.orders[].consignee.identification | stops[type=DELIVERY].location.name | |
| shipment.orders[].consignee.name | stops[type=DELIVERY].location.name | |
| shipment.orders[].consignee.address1 | stops[type=DELIVERY].location.address.address | |
| shipment.orders[].consignee.address2 | N/A | |
| shipment.orders[].consignee.country | stops[type=DELIVERY].location.address.country | |
| shipment.orders[].consignee.postalCode | stops[type=DELIVERY].location.address.postal_code | |
| shipment.orders[].consignee.city | stops[type=DELIVERY].location.address.city | |
| shipment.orders[].consignee.latitude | stops[type=DELIVERY].location.latitude | |
| shipment.orders[].consignee.longitude | stops[type=DELIVERY].location.longitude | |
| shipment.orders[].consignee.instructions | N/A | |
| shipment.orders[].consignee.dates[].qualifier | N/A | Fixed value "PLANNED" |
| shipment.orders[].consignee.dates[].dateTime | stops[type=DELIVERY].planned_date + planned_time_window_start | |

## Handling Units
| Field | Source | Notes |
|-------|--------|-------|
| shipment.orders[].handlingUnits[].packagingQualifier | line_items[].package_type | Direct mapping |
| shipment.orders[].handlingUnits[].grossWeight | line_items[].package_weight | Weight per unit |
| shipment.orders[].handlingUnits[].width | line_items[].width | Direct mapping in CM |
| shipment.orders[].handlingUnits[].length | line_items[].length | Direct mapping in CM |
| shipment.orders[].handlingUnits[].height | line_items[].height | Direct mapping in CM |
