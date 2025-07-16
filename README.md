# IntegrationSandbox

## General idea
Data integration use cases are complex and involve various systems and services. Testing out new data integration tooling can be a challenge without access to such services and systems. Setting up these systems and services just for testing out a new tool takes some heavy lifting.

I want to be able to test various data integration use cases without actually setting up full-blown services. 
My solution is to create a sandbox with mock services. I want to be able to test the following features of a integration platform:
- receive messages via a API/web-hook
- transform messages / perform a data mapping
- send messages to a API
- handle files
- conditional routing
- batch processing
- scheduling
- error handling
- authentication
- rate limiting

## example flow
Mocking an transport order flow from a TMS to a Carrier via a broker / visibility platform.

1. To trigger the process a 'trigger' controller will receive an event:

```
POST http://integration.sandbox/trigger/orders/

{
  target_url:"https://external-integration-service.com/tms/out",
  count: 10,
}
```
2. The controller will then generate mock order data, save it to a database and send messages to the target.
1. The integration service will then process the order and send a transformed message to the mocked visibility platform.
1. The mocked visibility platform will validate the response based on the data that was saved and some business rules for the data mappings.
1. A similar trigger to the first one will generate and send milestone data (basic tracking info or a POD) to the integration service.
1. The integration service will then process the milestone and send a transformed message to the mocked TMS.
1. Last, the mocked TMS will validate the milestones received.

 
## Requirements and things I want to use:
- Python 3.13  (latest stable version at this time)
- uv package manager
- ruff linter
- Faker for generating fake data
- FastAPI for the API's
- sqlite3

