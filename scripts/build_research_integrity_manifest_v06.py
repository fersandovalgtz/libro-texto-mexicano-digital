#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.6 for the v0.1.0-rc.1 public release cut.

This wrapper extends the frozen technical/scientific 0.5 critical set with the
release identity, adopted licenses, reproducibility package, and the scripts/
workflows that enforce release integrity. Human-reference/model outputs remain
outside the critical set until their preregistered gates are legitimately
crossed.
"""
from __future__ import annotations

import build_research_integrity_manifest as base

base.VERSION = 'LTMD_INTEGRITY_0.6'

RELEASE_CRITICAL = [
    'VERSION',
    'CHANGELOG.md',
    'LICENSE',
    'DATA_LICENSE.md',
    'requirements-release.txt',
    'docs/METHOD_INDEX.md',
    'docs/RELEASE_NOTES_v0.1.0-rc.1.md',
    'docs/REPRODUCIBILITY_ENVIRONMENT_0_1.md',
    'docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md',
    'docs/RELEASE_OUTPUTS_0_1.md',
    'docs/RIGHTS_PUBLICATION_MATRIX_0_2.md',
    'docs/LICENSE_DECISION_MEMO_0_1.md',
    'scripts/check_release_candidate.py',
    'scripts/build_research_integrity_manifest.py',
    'scripts/build_research_integrity_manifest_v06.py',
    '.github/workflows/check-release-candidate.yml',
    '.github/workflows/build-research-integrity-manifest.yml',
]

for path in RELEASE_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)

if __name__ == '__main__':
    base.main()
