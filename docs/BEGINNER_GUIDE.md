# Beginner Guide: Standalone PV System Design

## 1. What does this project design?

An off-grid solar PV system usually contains PV modules, a charge controller or hybrid inverter, a battery bank, an inverter and protection/wiring. The objective is to estimate the component sizes needed to supply a defined load profile under a chosen solar resource and autonomy target.

This repository provides a first-pass calculation tool. It is not a final electrical design or a substitute for a qualified engineer.

## 2. Start with the load, not the PV panel

List every appliance and record:
- rated power (W);
- number of units;
- hours of use per day;
- time of use;
- whether it is AC or DC;
- starting/surge demand for motors or compressors.

For each appliance:

`Daily energy (Wh) = quantity × rated power (W) × hours/day`

Sum appliance energy and divide by 1,000 to obtain kWh/day. A load profile should also show when the power is consumed; daily energy alone does not describe peak load or battery cycling.

## 3. Key terms

- **Peak sun hours (PSH):** daily solar irradiation expressed as equivalent hours at 1 kW/m². It varies by location, season, tilt and weather.
- **System derate:** aggregate allowance for system losses. A single factor is convenient for screening but a detailed design should itemise losses.
- **Depth of discharge (DoD):** fraction of nominal battery capacity intentionally used.
- **Autonomy:** number of days the system should operate with little or no PV charging.
- **Inverter kW/kVA:** real and apparent power are not the same; power factor matters.
- **Surge rating:** short-duration capacity needed to start motors and compressors.
- **LCOE:** discounted lifetime cost divided by discounted lifetime electricity delivered.

## 4. Run the example

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
python scripts/run_design.py
```

The default hourly load profile is synthetic. Change the configuration only after understanding the units and design implications.

## 5. Interpret the outputs

The script estimates daily energy, peak load, PV capacity, battery energy, battery ampere-hours and inverter apparent power. These are preliminary values.

Before selecting hardware, verify:
- module Voc at the minimum design temperature;
- module Isc and controller maximum input current;
- string count and maximum DC voltage;
- battery chemistry, voltage window, C-rate, temperature and cycle life;
- inverter continuous and surge curves;
- DC/AC cable ampacity and voltage drop;
- fuse/breaker ratings, disconnection, grounding and surge/lightning protection;
- installation method, enclosure/IP rating and environmental conditions.

## 6. Solar resource for Bangladesh

Use a recognised resource dataset at the actual site. Global Solar Atlas and NASA POWER are potential starting points for regional screening. Monthly and seasonal patterns matter; one annual-average PSH value can hide the worst month. Do not treat a country-average resource as a site survey.

## 7. Why the hourly profile matters

Two households can use the same 10 kWh/day but have different peak loads. One may use energy evenly through the day; another may run a pump, refrigerator and other appliances at the same time. Their inverter and battery requirements can be very different.

A stronger extension is an hourly dispatch simulation: calculate PV generation by hour, serve the load, charge/discharge the battery, track state of charge, unmet energy and curtailment.

## 8. Common mistakes

- Sizing from daily energy alone without checking peak and surge power.
- Using panel nameplate power as actual daily energy.
- Ignoring inverter and battery losses.
- Assuming battery nominal capacity equals usable capacity.
- Ignoring seasonal solar variability and shading.
- Selecting series modules using uncorrected STC Voc only.
- Using a voltage-drop cable calculation as a complete cable selection.

## 9. Design limitations

The simplified project does not replace a full hourly simulation, component datasheets or electrical code review. Use it for transparent screening, learning and early comparison—not procurement or construction.
