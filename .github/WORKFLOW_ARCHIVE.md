# GitHub Actions workflow archive

This repository intentionally keeps only the canonical continuous-integration workflows executable under `.github/workflows/`.

The directory `.github/legacy-workflows-v0.2.0/` is an exact Git-tree preservation of the workflow set present in LTMD `v0.2.0`. These files are retained as computational provenance and reproducibility recipes, but GitHub Actions does not execute workflows outside `.github/workflows/`.

## Active workflow policy

The active surface is limited to:

- `repository-quality.yml` — repository quality gate;
- `release-preflight.yml` — scientific release preflight;
- `test-ltmd-analytics.yml` — LTMD Analytics tests;
- `automated-benchmark.yml` — deterministic automated benchmark contracts.

Any future active workflow must scope `push` events to explicit branches (normally `main`) so Git tag creation cannot trigger path-only legacy pipelines. Default permissions should remain read-only. Workflows that generate derived research products should prefer artifacts or reviewed pull requests instead of pushing directly to `main`.

## Why this archive exists

Creating the `v0.2.0` tag exposed a legacy Actions design in which many path-filtered `push` workflows had no branch restriction. GitHub does not evaluate path filters for tag pushes, so the tag activated a large historical workflow surface. Archiving the legacy set preserves scientific traceability while removing that operational failure mode.
