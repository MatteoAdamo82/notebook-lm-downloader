# Working on nbdl

## Before modifying nbdl.py

Read `nbdl.py.ctx`. It documents the tensions (constraints that must not be broken) and the intended workflows.

## Critical: the monkey-patch

Lines 25-34 of `nbdl.py` patch `Notebook.from_api_response` to fix a bug in notebooklm-py (sources_count always returns 0). **Do not remove it** unless you've verified the upstream library has shipped the fix. Check `todos` in `nbdl.py.ctx` for status.

## Generating tests

This project has no test suite yet. To generate one:

> "Read `nbdl.py` and `nbdl.py.ctx`. Implement the `conceptualTests` as pytest tests. Mock `NotebookLMClient` and its async methods."

## After modifying nbdl.py

Run the sync prompt:
> "I've modified `nbdl.py`. Read the updated file and `nbdl.py.ctx` and tell me what needs updating in the `.ctx`."

## Stack

- Python 3.9+
- async/await throughout — all I/O is async
- `rich` for terminal output, `prompt_toolkit` for interactive input
- `notebooklm` (notebooklm-py) for API access — authenticated via `from_storage()`
- No test suite yet
