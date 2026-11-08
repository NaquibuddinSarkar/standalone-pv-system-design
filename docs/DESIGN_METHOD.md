# Preliminary design method

1. Convert the hourly load profile to daily energy and determine peak demand.
2. Estimate PV array rating as daily energy divided by peak-sun-hours and a system derate.
3. Estimate nominal battery energy using autonomy, allowable depth of discharge and battery efficiency.
4. Convert battery kWh to Ah at the selected nominal DC voltage.
5. Estimate inverter capacity from simultaneous peak load, power factor and a design margin.
6. Conduct lifecycle economics using capital cost, annual savings, O&M, replacements and discount rate.

## Engineering checks still required

The current toolkit is a first-pass sizing calculator. A real design needs site-specific irradiation and temperature, shading, seasonal autonomy, charge controller voltage/current windows, battery chemistry and C-rate limits, inverter surge duty, cable ampacity and voltage drop, protection coordination, grounding, lightning/surge protection, applicable electrical codes and qualified engineering review. Never size wiring or protection from the simplified outputs alone.

The demo load profile is synthetic.
