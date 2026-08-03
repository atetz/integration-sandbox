# UI built with HTMX + daisyUI via direct service calls, not NiceGUI

The Minimalistic UI (issue #23) needed a way to run manual test flows without hand-crafted HTTP requests. We chose HTMX + server-rendered Jinja templates (styled with daisyUI) in a dedicated `ui/` module that calls the existing `trigger`/`tms`/`broker` service functions directly in-process, over NiceGUI, because this is a single-container FastAPI app where a second Python UI framework with its own component model would add a competing abstraction layer instead of extending the one already there.

**Considered options**: NiceGUI (full Python reactive UI framework — more power, but a second paradigm and a heavier dependency); routing UI actions through the app's own HTTP API instead of calling services directly (adds a redundant network hop for zero benefit in a single process).
