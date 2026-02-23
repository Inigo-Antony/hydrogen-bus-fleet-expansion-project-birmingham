# Birmingham H₂ Bus Fleet Expansion – Techno-Economic Analysis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python model for the techno-economic analysis of hydrogen refuelling infrastructure simulating Birmingham's 140-bus FCEV fleet expansion, including sensitivity analysis on electricity price, diesel breakeven pricing, and NPV/IRR calculations incorporating carbon cost benefits.

This work extends a coursework report done during masters in Sustainable Energy Systems at the University of Birmingham and IIT Madras.

---

## Overview

- A **12 MWe PEM electrolyser expansion** at Tyseley (~£15.75M CAPEX)
- A **4-station HRS network** across Birmingham depots (~£7.25M CAPEX)
- **GH₂ tube trailer delivery** from centralised production to satellite refuelling points

### Key Results (Baseline: £57/MWh electricity, £50/t CO₂e)

| Metric | Value |
|--------|-------|
| Daily H₂ demand (140 buses) | 3,570 kg/day |
| Total CAPEX | £23.0M |
| LCOH at dispenser | £6.76/kg |
| Annual H₂ fuel cost | £8.81M/yr |
| Annual diesel equivalent | £13.17M/yr |
| CO₂ reduction vs diesel | **80%** (11,061 t/yr) |
| NPV (20yr, 8% WACC) | £24.4M |
| IRR | 20.5% |
| Simple payback | 4.8 years |

---

## Repository Structure

```
├── main.py                          # Run full analysis + generate all figures
├── Birmingham_H2_Bus_Analysis.ipynb # Jupyter notebook (interactive)
├── requirements.txt
├── ASSUMPTIONS.md                   # All modelling assumptions documented
├── Hydrogen Bus Fleet Expansion Birmingham.pdf  #report on the project
├── outputs/                         # Generated figures (9 PNG files)
└── src/
    ├── parameters.py                # All baseline constants (fully documented)
    ├── demand.py                    # H₂ demand calculations
    ├── infrastructure.py            # CAPEX: electrolyser + HRS
    ├── economics.py                 # LCOH, NPV, IRR, breakeven
    ├── emissions.py                 # Well-to-Wheel CO₂ analysis
    └── sensitivity.py               # All sensitivity analyses + figure generation
```

---

## Figures Generated

| File | Description |
|------|-------------|
| `lcoh_vs_electricity.png` | Stacked LCOH components vs electricity price |
| `annual_cost_vs_elec.png` | H₂ vs diesel annual fleet cost crossover |
| `breakeven_diesel.png` | Diesel price parity vs electricity price (multiple carbon scenarios) |
| `npv_vs_elec_carbon.png` | NPV sensitivity to electricity & carbon price |
| `irr_vs_elec.png` | IRR vs electricity price with WACC hurdle rate |
| `npv_heatmap.png` | 2D NPV heatmap: electricity price × carbon price |
| `emissions_comparison.png` | WtW annual CO₂e bar chart + H₂ pathway breakdown |
| `capex_breakdown.png` | Infrastructure CAPEX waterfall |
| `lcoh_sensitivity_tornado.png` | Tornado chart: ±20% one-at-a-time parameter sensitivity |

---

## Quickstart

**1. Clone and install dependencies**

```bash
git clone https://github.com/Inigo-Antony/hydrogen-bus-fleet-expansion-project-birmingham.git
cd hydrogen-bus-fleet-expansion-project-birmingham
pip install -r requirements.txt
```

**2. Run the full analysis**

```bash
python main.py
```

This prints a full results summary to the console and saves all 9 figures to `./outputs/`.

**3. Interactive notebook**

```bash
jupyter notebook Birmingham_H2_Bus_Analysis.ipynb
```

**4. Modify parameters**

All constants are centralised in `src/parameters.py`. Change the baseline electricity price, fleet size, discount rate, or any other assumption there — all downstream calculations update automatically.

```python
# Example: assess impact of cheaper offshore wind PPAs
from src.economics import calculate_lcoh
lcoh_40 = calculate_lcoh(electricity_price_gbp_mwh=40)
print(f"LCOH at £40/MWh: £{lcoh_40.total_dispensed_cost_gbp_kg:.2f}/kg")
```

---

## Sensitivity Analyses

### Electricity Price (£20–£120/MWh)
The single largest driver of LCOH. At **£20/MWh** (aggressive offshore wind PPA), H₂ at the dispenser drops to ~£4/kg, well below diesel parity. At **£120/MWh** (grid industrial tariff), cost rises to ~£12/kg, making diesel strongly preferable on fuel cost alone.

### Breakeven Diesel Price
At the baseline electricity price of £57/MWh and zero carbon price, diesel must be above ~**£0.73/L** for the H₂ fleet to be fuel-cost competitive. At £50/t carbon price, this threshold drops to ~£0.70/L — well below current UK pump prices (£1.40/L), meaning **the H₂ fleet is already cost-competitive at baseline parameters**.

### NPV / IRR
- **IRR of 20.5%** at baseline exceeds the 8% WACC, indicating positive economic returns even without subsidy.
- NPV remains positive for electricity prices up to ~£115/MWh at £50/t carbon price.
- The NPV heatmap shows the **investment is robust across a wide parameter space**, becoming negative only at very high electricity prices combined with low carbon prices.

---

## Methodology

### LCOH Model

```
LCOH_dispensed = Production_LCOH + Transport + HRS_OPEX

Production_LCOH = Electricity_cost + CAPEX_amortised + Non-energy_OPEX + Stack_replacement

where:
  Electricity_cost = η [kWh/kg] × price [£/kWh]
  CAPEX_amortised  = CAPEX × CRF(r, n) / annual_production_kg
  CRF              = r(1+r)^n / ((1+r)^n - 1)   [Capital Recovery Factor]
```

### NPV / IRR
Cash flows: year 0 = −CAPEX; years 1–20 = fuel savings + carbon savings.

```
Annual_benefit = (Diesel_cost − H2_cost) + (CO2_saved_tonnes × carbon_price_£/t)
NPV = Σ [Annual_benefit / (1+r)^t] − CAPEX
```

IRR solved by bisection on NPV(r) = 0.

### WtW Emissions

```
H2_EF = (electrolyser_kWh/kg × grid_gCO2e/kWh)   [production]
      + (HRS_kWh/kg × grid_gCO2e/kWh)              [compression]
      + transport_factor                             [truck delivery]
```

---

## References

1. Apostolou & Xydis (2019). *A literature review on hydrogen refuelling stations and infrastructure.* Renewable and Sustainable Energy Reviews, 113.
2. Genovese & Fragiacomo (2023). *Hydrogen refueling station: Overview of the technological status.* Journal of Energy Storage, 61.
3. Mayer et al. (2019). *Techno-economic evaluation of hydrogen refueling stations with liquid or gaseous stored hydrogen.* Int. Journal of Hydrogen Energy, 44(47).
4. Wang et al. (2019). *Life-cycle greenhouse gas emissions of onshore and offshore wind turbines.* Journal of Cleaner Production, 210.
5. Wrightbus. *StreetDeck Hydroliner FCEV product datasheet.*
6. Tyseley Energy Park. *Tyseley Refuelling Hub.* https://www.tyseleyenergy.co.uk

Full reference list: see original report (`ASSUMPTIONS.md`).

---

## About

**Inigo Antony Michael Selvam**  
MSc Sustainable Energy Systems | University of Birmingham / IIT Madras  

---

*Built as part of an academic portfolio demonstrating energy systems modelling and techno-economic analysis capabilities.*
