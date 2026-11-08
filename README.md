# Standalone PV System Design

An engineering calculation toolkit for preliminary standalone solar PV sizing and techno-economic analysis. The complete project source package is provided in [source-code.zip](./source-code.zip).

## What is included

The source archive contains Python sizing and economics modules, a load-profile CSV, design configuration, a Jupyter walkthrough, a command-line design runner, tests and engineering-method documentation.

The calculations cover load demand, PV array sizing, battery energy and autonomy, inverter capacity, preliminary DC-side sizing and lifecycle economics.

## Quick start

Download and extract [source-code.zip](./source-code.zip), then run from the extracted project directory:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
python scripts/run_design.py
```

## Engineering limitations

The default load profile and configuration are illustrative. Actual design requires site-specific solar resource data, temperature and shading analysis, applicable electrical codes, certified equipment datasheets, cable/voltage-drop and protection studies, battery chemistry limits, installation losses and qualified engineering review. The code is a preliminary sizing aid, not a construction-ready design.

**No GitHub Actions or CI workflow is included, as requested.** Local tests are retained for manual verification.

[Download complete source package](./source-code.zip)
