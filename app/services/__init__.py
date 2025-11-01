"""Service package namespace.

Avoid importing submodules at package import time to prevent side effects
when the package is imported as part of module resolution (e.g., uvicorn).
"""

__all__ = []