# Data Dictionary and Engineering Inputs

## Hourly load profile

File: `data/demo/load_profile_synthetic.csv`

| Field | Type | Unit | Meaning | Validation |
|---|---|---|---|---|
| hour | integer | 0–23 | Hour index in the representative day | Unique and within 0–23 |
| load_w | numeric | W | Aggregate load during the hour | Non-negative and finite |

The demonstration profile is synthetic. For a real system, document the measurement date range, sampling interval, meter accuracy, missing data, seasonal coverage and whether demand is measured at AC or DC side.

## Configuration file

File: `config/design.json`

| Parameter | Unit | Meaning | Important note |
|---|---|---|---|
| peak_sun_hours | h/day | Solar resource proxy | Use site/month-specific values |
| autonomy_days | days | Required no-sun autonomy | Define critical load and service requirement |
| battery_voltage_v | V DC | Nominal battery bus | Must be compatible with inverter/controller |
| system_derate | fraction | Aggregate PV-side system derate | Document itemised losses when known |
| depth_of_discharge | fraction | Allowed usable battery fraction | Technology and warranty dependent |
| battery_efficiency | fraction | Round-trip/discharge simplification | Define whether one-way or round-trip |
| power_factor | fraction | Load power factor for kVA estimate | Use actual equipment values if available |
| inverter_margin | multiplier | Preliminary sizing margin | Does not replace surge analysis |

## Additional data required for engineering design

- appliance inventory and measured load curves;
- critical/noncritical load classification;
- site coordinates, tilt, azimuth, shading and horizon;
- monthly irradiation and ambient/module temperature;
- module datasheets (Voc, Isc, Vmp, Imp, temperature coefficients);
- inverter/charger datasheets and surge duration;
- battery chemistry, voltage limits, C-rate, temperature and warranted cycles;
- cable routes, material, installation method, ambient temperature and grouping;
- short-circuit levels, protection devices, earthing and applicable standards.

Do not treat the default configuration as a Bangladesh-wide standard design.
