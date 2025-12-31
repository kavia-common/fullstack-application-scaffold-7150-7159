"""Top-level package for the backend source tree.

Keeping `src/` as a proper Python package ensures imports like `src.api.main`
work consistently across:
- Uvicorn execution
- pytest collection
- IDE/static analysis
"""
