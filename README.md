# Standalone PV System Design

A preliminary engineering toolkit for off-grid solar PV sizing and techno-economic screening.

## Project contents

- `src/standalone_pv_design/sizing.py`: daily energy, PV array rating, battery nominal capacity, inverter rating and first-pass charge-controller current.
- `src/standalone_pv_design/economics.py`: discounted lifecycle cash-flow helper.
- `scripts/run_design.py`: loads the illustrative hourly profile and design configuration.
- `config/design.json`: solar resource, autonomy, voltage, derating and equipment assumptions.
- `data/demo/load_profile_synthetic.csv`: 24-hour synthetic load profile.
- `notebooks/01_standalone_pv_sizing_walkthrough.ipynb`: interactive design walkthrough.
- `tests/`: manual calculation and validation tests.
- `source-code.zip`: downloadable CI-free source package.

## Quick start

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

The sizing formulas are preliminary. Actual design requires site-specific solar resource and temperature data, shading and seasonal analysis, certified equipment datasheets, battery chemistry and C-rate constraints, inverter surge requirements, wiring ampacity and voltage-drop calculations, protection coordination, grounding, lightning/surge protection, applicable standards and qualified engineering review.

The bundled load profile and configuration are illustrative, not a construction-ready design. Do not use the simplified current estimate as a final cable or protection selection.

No GitHub Actions or CI workflow is configured. Tests are available for manual local execution.

## Licence

MIT. See [LICENSE](LICENSE).
