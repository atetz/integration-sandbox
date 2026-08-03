# Integration Sandbox

Simulates data integration scenarios between Transport Management Systems (TMS) and brokers (visibility platforms), so integration flows can be tested without standing up real external systems.

## Language

**Seed**:
Generate mock TMS shipments or broker events and store them in the database only — no dispatch to an external target.
_Avoid_: Generate, create

**Trigger**:
Generate mock TMS shipments or broker events, store them, and dispatch them to an external target URL.
_Avoid_: Send, dispatch

**Nuke**:
Delete every row from all tables, resetting the sandbox to an empty database. Schema and running app are untouched.
_Avoid_: Reset, clear, wipe
