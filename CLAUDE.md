# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Integration Sandbox is a Python 3.13 project that simulates data integration scenarios between Transport Management Systems (TMS) and brokers (visibility platforms). It provides mock services to test integration flows without setting up full-blown external systems.

### End-goal
Single-developer containerized testing tool for data integration flows.


## Development Commands

### Package Management
- **Install dependencies**: `uv install` 
- **Run application**: `uv run fastapi dev integrationsandbox/main.py`
- **Run tests**: `uv run pytest`
- **Lint code**: `uv run ruff check`
- **Format code**: `uv run ruff format`

## Architecture

### Architecture Philosophy:
  - Appropriately simple: SQLite, direct imports, minimal abstraction layers
  - Container-first design: Stateless, fast setup/teardown, single file database
  - Testing-focused: Mock services that validate real data transformations
  - Operational simplicity: Single maintainer, minimal deployment complexity

### Core Components
- **FastAPI Application**: Main entry point in `integrationsandbox/main.py` with health check endpoint
- **Database**: SQLite database managed through `infrastructure/database.py` with setup function
- **API Prefix**: All endpoints use `/api/v1` prefix

### Domain Modules

#### Trigger Module (`trigger/`)
- Generates and dispatches mock data to external systems
- **Controller**: POST endpoints for `/trigger/shipments/` and `/trigger/events/`
- **Service**: Creates mock TMS shipments and broker events using factories
- **Models**: Event and shipment trigger request models

#### Broker Module (`broker/`)
- Receives and validates broker orders from external integration services
- **Controller**: POST endpoint `/broker/order/` that validates incoming orders
- **Service**: Complex validation logic comparing transformed data against original TMS data
- **Models**: Comprehensive broker order message models with nested structures
- **Repository**: Database operations for broker data

#### TMS Module (`tms/`)
- Models and data access for Transport Management System entities
- **Models**: TMS shipment, stop, line item, and customer models
- **Repository**: Database operations for TMS shipment data
- **Factories**: Generates realistic fake TMS data using Faker

### Key Architecture Patterns

#### Data Mapping & Validation
The broker service implements sophisticated data transformation validation:
- `apply_mapping_rules()`: Transforms TMS shipment data to expected broker format
- `get_transformed_data()`: Extracts data from incoming broker orders
- `compare_mappings()`: Deep comparison using DeepDiff to validate transformations
- Package type mapping from TMS enums to broker qualifiers

#### Mock Data Generation
- Faker-based factories for generating realistic test data
- Consistent data relationships (e.g., shipment references match across systems)
- Configurable data volume through trigger count parameters

#### Database Design
- Simple SQLite schema with JSON columns for flexible data storage
- Tables: `tms_shipment` and `broker_event` with unique constraints
- Connection management through context managers

## Integration Flow

The typical integration test flow:
1. **Trigger**: POST to `/trigger/shipments/` generates TMS shipments and sends to external URL
2. **External Processing**: Integration service processes and transforms the data
3. **Validation**: POST to `/broker/order/` validates the transformed data against original TMS data
4. **Event Processing**: Similar flow for tracking events and milestones

## Testing Strategy

- **pytest** with fixtures for common test data
- Test fixtures for both TMS and broker line items in `tests/conftest.py`

## Configuration

- **Python 3.13** with `uv` package manager
- **Ruff** for linting with specific rule selection (E4, E7, E9, F)
- **FastAPI** with CORS middleware enabled for all origins (development setup)
- **SQLite** database file located at `integrationsandbox/infrastructure/db.sqlite3`

## Data Mapping Documentation

Detailed field mapping specifications are documented in `docs/integrations/tms-to-visibility.md` covering:
- Message metadata mapping
- Shipment and order detail transformations  
- Location mapping (pickup/delivery)
- Package type conversions
- Time window qualifiers

## Assistant role
- You are a highly realistic and straightforward assistant.
- Your goal is to be clear, direct, and brutally honest.
- Do not sugarcoat. If an idea is unworkable, strange, or misguided, say so plainly. If something is poorly done, say how and why.
- Skip excessive pleasantries, hedging, or unnecessary “please” behavior. If something can be improved, say exactly how without softening it. If something is done well, acknowledge it simply and move on. 
- You can use short, punchy sentences. Be efficient. Be sharp. Be real.  
- Your tone should feel like a candid colleague, constructive but not coddling
- Do not generate code unless explicitly asked.