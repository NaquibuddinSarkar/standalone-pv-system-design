# Standalone Solar PV System Design

A preliminary engineering toolkit for sizing an off-grid solar photovoltaic (PV) system from an hourly electrical load profile. It estimates daily energy, PV array capacity, battery storage, inverter rating and selected balance-of-system checks, then provides a first-pass lifecycle economic assessment.

> **Safety and design status:** this is a planning and learning tool, not a construction-ready electrical design. Final equipment selection, protection, cabling, earthing, lightning/surge protection, structural design and commissioning must be reviewed by a qualified electrical engineer using site-specific data and applicable standards.

## Start here

Read [the beginner guide](docs/BEGINNER_GUIDE.md) before editing the configuration.

### Quick start

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
pytest -q
python scripts/run_design.py
```

The included hourly profile is synthetic. Replace it with measured load data before using the results for a real site.

## Design workflow

1. **Build a load inventory:** list each AC/DC appliance, rated power, quantity, operating hours and expected coincidence.
2. **Create a time profile:** represent hourly or sub-hourly demand; identify daily energy and maximum coincident load.
3. **Estimate solar resource:** use site-specific irradiation data and account for seasonality, shading, tilt, orientation and temperature.
4. **Size the PV array:** estimate the DC array capacity required to meet energy demand after losses.
5. **Size battery storage:** set autonomy, usable depth of discharge, battery efficiency and bus voltage.
6. **Size the inverter:** check continuous real/apparent power, power factor, motor starting and surge.
7. **Check controller and wiring:** verify cold-corrected open-circuit voltage, short-circuit current, cable ampacity, voltage drop and protection.
8. **Evaluate economics:** estimate capex, replacement, O&M, delivered energy, discounted cost and LCOE.

## Main equations

### Daily energy

For hourly loads in watts:

`E_day (kWh/day) = sum(hourly load in W) / 1000`

### PV array

`PV size (kWp) = design daily energy (kWh/day) / [peak sun hours × system derate]`

The derate factor is an aggregate planning assumption. In a real design, explicitly account for module temperature, dust/soiling, mismatch, DC wiring, controller, battery and inverter losses instead of hiding all losses in one number.

### Battery storage

`Battery nominal kWh = daily energy × autonomy days / (DoD × battery efficiency × inverter efficiency)`

This is a first-pass energy calculation. Battery chemistry, permitted C-rate, temperature, ageing, end-of-life capacity, low-voltage cut-off and manufacturer requirements can change the result.

### Inverter rating

The tool estimates a preliminary continuous rating from peak load and sizing margin. Check both kW and kVA, power factor, motor starting current, surge duration, harmonics and the inverter's overload curve.

## Data sources and standards to consult

- **Global Solar Atlas / World Bank Bangladesh solar resource data:** https://datacatalog.worldbank.org/search/dataset/0039840/bangladesh-solar-irradiation-and-pv-power-potential-map
- **NASA POWER daily solar and meteorological API documentation:** https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- **SREDA solar component standards for the net-metering programme:** https://sreda.portal.gov.bd/pages/static-pages/6922db99933eb65569e0b2bc
- **Bangladesh Net Metering Guideline 2025:** https://nem.powerdivision.gov.bd/Faq

These references help identify resource data and applicable component standards; they do not replace project-specific engineering review. A standalone system may not be a net-metered system, but equipment safety and electrical standards remain relevant.

## Outputs and interpretation

The script prints:
- daily load energy and peak load;
- preliminary PV kWp;
- battery nominal kWh and Ah at the selected bus voltage;
- inverter continuous/surge estimate;
- a preliminary controller current estimate;
- lifecycle cost and LCOE (where configured).

Do not interpret a rounded module count or cable cross-section as a final procurement specification. Check actual module datasheets, temperature-corrected Voc, Isc, string limits, controller current limits, conductor ampacity and protection coordination.

## Repository structure

```text
config/       editable engineering and economic assumptions
data/demo/    synthetic hourly load profile
docs/         beginner guide, design method and data provenance
notebooks/    interactive design walkthrough
scripts/      reproducible sizing calculation
src/          reusable sizing and economic functions
tests/        unit tests
outputs/      generated results
```

## Limitations

The current simplified model does not fully simulate hourly battery dispatch, state of charge, unmet load, loss-of-load probability, seasonal PV production, shading, battery degradation, temperature-corrected module strings, inverter efficiency curves, protection coordination or detailed cable installation conditions. A stronger project-specific design should add hourly dispatch simulation and a full equipment schedule.

## Reproducibility

Run `pytest -q` to execute the manual unit tests. No GitHub Actions or CI workflow is configured.

## Licence

MIT for the code. Solar resource and third-party data remain subject to their own licences.
