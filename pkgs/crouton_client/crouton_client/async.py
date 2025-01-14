import warnings
import importlib

warnings.warn(
    "async.py is deprecated. Please use `from crouton_client.client import CroutonClient` instead.",
    DeprecationWarning,
    stacklevel=2
)

def __getattr__(name):
    if name == "AsyncCroutonClient":
        module = importlib.import_module("crouton_client.client")
        return getattr(module, "CroutonClient")
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
