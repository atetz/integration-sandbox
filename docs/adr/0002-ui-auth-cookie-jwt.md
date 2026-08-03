# UI session auth reuses the existing JWT via a cookie, not a separate session system

The UI needs browser-based login with a configurable password, but the existing `tms`/`broker`/`trigger` auth is bearer-JWT-in-header, which browsers don't attach to plain navigations. We reuse the same `authenticate_user`/`create_access_token`/`jwt_secret_key` machinery and carry the token in an `HttpOnly` cookie instead, verified with the same `jwt.decode` logic, rather than building a second, independent session mechanism alongside it.

**Consequences**: UI sessions use a separate `ui_session_expire_minutes` setting (longer-lived) distinct from the API's `jwt_expire_minutes`; the cookie's `Secure` flag defaults on but is configurable, since `Secure` cookies aren't sent over plain HTTP on non-localhost deployments.
