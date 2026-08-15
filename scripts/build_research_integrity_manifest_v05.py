#!/usr/bin/env python3
"""Finalize LTMD_INTEGRITY_0.5 with the central methodological index.

This thin wrapper extends the already frozen 0.5 critical set without changing
its semantic version: METHOD_INDEX became part of the visible methodological
surface after the initial 149/149 cut and must therefore be hashed as critical.
"""
from __future__ import annotations

import build_research_integrity_manifest as base

INDEX = 'docs/METHOD_INDEX.md'
if INDEX not in base.CRITICAL:
    base.CRITICAL.append(INDEX)

if __name__ == '__main__':
    base.main()
