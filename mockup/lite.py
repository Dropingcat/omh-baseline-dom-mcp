"""WR-ADD (L0+L1): the lite (local_single_owner) profile.

This module is now a thin re-export shim over :mod:`mockup.claim_entry`, which
holds the shared claim-entry implementation used by both profiles (TD-DOM-22.1).
All public names remain available here for backward compatibility.
"""
from .claim_entry import *  # noqa: F401,F403