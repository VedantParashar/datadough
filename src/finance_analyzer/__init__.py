"""The old name of the `datadough` package. Import `datadough` instead; this shim will be removed."""

import warnings

from datadough import *  # noqa: F403
from datadough import __all__  # noqa: F401

warnings.warn(
    "finance_analyzer is now datadough: use `import datadough`. The old name will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)
