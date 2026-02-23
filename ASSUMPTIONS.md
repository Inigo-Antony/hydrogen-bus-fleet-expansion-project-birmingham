# Assumptions & Methodology Notes

> **Project:** Birmingham H₂ Bus Fleet – Techno-Economic Analysis  
> **Author:** Inigo Antony Michael Selvam, MSc Sustainable Energy Systems, University of Birmingham / IIT Madras  

This document records all modelling assumptions, their basis, and known limitations.
It is intended for anyone reviewing the model (academics, interviewers, collaborators).

---

## 1. Fleet & Operations

| Parameter | Value | Basis |
|-----------|-------|-------|
| Total fleet size | 140 buses | Report specification |
| Existing fleet | 20 buses | Operational since late 2021 (NXWM) |
| Bus model | Wrightbus StreetDeck Hydroliner FCEV | Birmingham City Council pilot |
| H₂ tank capacity | 27 kg @ 350 bar | Wrightbus product datasheet |
| Maximum range | 300 miles (≈ 483 km) | Wrightbus product datasheet |
| Fuel economy | **8.5 kg / 100 km** | Midpoint between spec (9 kg/100 km) and BCC Full Business Case (8 kg/100 km) |
| Daily mileage | **300 km / bus / day** | Cited in NX West Midlands operational data |
| Operating days | 365 days/yr | Assumed 24/7/365 fleet availability; no scheduled maintenance downtime |

**Key limitation:** The 300 km/day and 8.5 kg/100 km assumptions together imply 25.5 kg consumed per day, leaving a minimal 1.5 kg buffer before the 27 kg tank is exhausted. This assumption holds only if buses return to depot before each refuel, which is typical for urban bus operations.

---

## 2. Hydrogen Production (Tyseley PEM Electrolyser)

| Parameter | Value | Basis |
|-----------|-------|-------|
| New electrolyser capacity | 12 MWe | Calculated: 2570 kg/day gap ÷ 267 kg/day/MWe; rounded up |
| Electrolyser yield | 267 kg H₂/day/MWe | Derived from existing 3 MWe unit → 1,000 kg/day |
| Specific energy consumption | **55 kWh / kg H₂** | Typical large-scale PEM (2023–2025); HHV efficiency ≈ 69% |
| Electrolyser cost | £750/kW | Adapted from $1,000/kW (IEA / PV-magazine, 2024) at 1.18 GBP/USD |
| BoP & installation | 75% of equipment cost | Mid-range industry estimate; typical range 50–100% |
| Electrolyser lifetime | 25 years | Standard design life for PEM systems |
| Non-energy OPEX | 2% CAPEX/yr | Industry consensus for electrolyser O&M |
| Stack replacement | 1.5%/yr annualised | Assuming stack replacement at ~10 years at 15% of CAPEX |
| Operating hours | 8,000 hr/yr | ≈ 91% availability; consistent with grid-connected electrolysis |

**Key limitation:** The 55 kWh/kg figure represents optimistic near-term performance. Real-world systems in 2024 operate at 55–65 kWh/kg. Higher values would increase LCOH proportionally to the electricity component.

---

## 3. Electricity Supply

| Parameter | Value | Basis |
|-----------|-------|-------|
| Baseline electricity price | £57/MWh | Back-calculated to reproduce reported LCOH of ~£10/kg (€12/kg) at an internally consistent level |
| Sensitivity range | £20–£120/MWh | Covers offshore wind PPA (low) to industrial grid tariff (high) |
| Carbon intensity | **35 gCO₂e/kWh** | Typical lifecycle emissions factor for UK offshore wind (Wang et al., 2019) |

**Note on electricity price:** The report uses an LCOH calculator (reference 15, ANZ Hydrogen Handbook) that quotes €9.69/kg for production. This is consistent with an electricity price of approximately €60–65/MWh. The £57/MWh baseline used here reflects the UK market context and gives an internally consistent model. In the sensitivity analysis this parameter is the single largest driver of LCOH variability.

---

## 4. Transport (GH₂ Tube Trailer Delivery)

| Parameter | Value | Basis |
|-----------|-------|-------|
| Transport pathway | Gaseous H₂ (GH₂) tube trailer | Report decision; appropriate for short-medium urban distances |
| Trailer payload | 1,000 kg @ 500 bar | High-pressure container trailer (report Section 3) |
| Transport cost | £0.85/kg (≈ €1.00/kg) | Thomas et al. (2019), adjusted to GBP |
| Transport CO₂ | 0.027 kg CO₂e/kg H₂ | Climatiq database, rigid truck 26–32t, diesel, urban Europe |

**Minimum deliveries required:** 3 satellite depots × 1 delivery/day each (at 1,000 kg/delivery) plus partial load deliveries. In practice, logistics planning would need to account for driver hours, maintenance windows, and demand surges.

**Liquid H₂ not selected:** The liquefaction energy penalty (~8 kWh/kg) and associated capital cost make LH₂ economically unviable at this scale (Apostolou & Xydis, 2019). The model does not include an LH₂ pathway.

---

## 5. HRS (Hydrogen Refuelling Stations)

| Parameter | Value | Basis |
|-----------|-------|-------|
| Station configuration | Cascade system, 2-dispenser (2D) | Thomas et al. (2019) — medium station |
| Station capacity | ~1,000 kg/day | Selected for alignment with satellite depot demand |
| CAPEX per station | €2.85M (≈ £2.42M) | Thomas et al. (2019), 2D trucked-in 20 MPa station |
| HRS OPEX | £1.04/kg (≈ €1.22/kg) | Thomas et al. (2019), 1,000 kg/day at 100% utilisation |
| Dispensing pressure | 350 bar (35 MPa) | Bus specification; pre-cooling to −20 °C per T20 protocol |
| New stations | 3 | Perry Barr, Yardley Wood, Acocks Green depots |

**Utilisation assumption:** 100% utilisation in the HRS OPEX figure is optimistic. Real utilisation during ramp-up phase would be lower, increasing the effective OPEX per kg. This is a standard boundary condition in techno-economic modelling.

---

## 6. Financial Model (NPV / IRR)

| Parameter | Value | Basis |
|-----------|-------|-------|
| CAPEX timing | Year 0 (lump sum) | Conservative: assumes full build before any revenue |
| Project life | 20 years | Consistent with HRS and electrolyser asset lifetimes |
| Discount rate (WACC) | 8% | Typical public infrastructure / energy project in UK |
| Benefit stream | Fuel savings + carbon savings | See below |
| Inflation | Not modelled | Real cash flows assumed (no nominal inflation adjustment) |
| Residual value | Zero | Conservative: no salvage value assumed |
| Subsidies | None | Baseline is unsubsidised; sensitivity analysis implicitly captures policy support via carbon price |

**Benefit stream calculation:**
- **Fuel savings** = Annual diesel fleet cost − Annual H₂ fleet cost
- **Carbon savings** = Annual CO₂e reduction (tonnes) × carbon price (£/tonne)
- Carbon price sensitivity range: £0–£200/tonne CO₂e
- UK ETS carbon price has historically ranged £20–£100/tonne; projections for 2040+ range to £150+

---

## 7. Emissions (Well-to-Wheel)

| Stage | Value | Basis |
|-------|-------|-------|
| Electrolysis | 55 kWh/kg × 35 gCO₂e/kWh = **1.925 kg CO₂e/kg H₂** | Electricity-based calculation |
| HRS operations | 4.21 kWh/kg × 35 gCO₂e/kWh = **0.147 kg CO₂e/kg H₂** | Genovese & Fragiacomo (2023) |
| Transport | **0.027 kg CO₂e/kg H₂** | Climatiq, urban diesel truck |
| **Total H₂ WtW** | **2.099 kg CO₂e/kg H₂** | Sum of above |
| Diesel bus WtW | **0.90 kg CO₂e/km** | DEFRA/BCC Full Business Case assumption |

**Scope boundary:** This is a Well-to-Wheel (WtW) boundary, covering fuel production, transport, station operations, and vehicle use. It does not include:
- Manufacturing emissions for buses (lifecycle/cradle-to-gate)
- Manufacturing emissions for electrolyser and HRS equipment
- End-of-life disposal

A full lifecycle assessment (LCA) would increase emissions for both pathways, but H₂ FCEV still demonstrates >70% reduction in most published LCAs.

---

## 8. Known Simplifications

1. **Fixed diesel price:** The model uses £1.40/L diesel as a static reference. In practice, diesel prices fluctuate, which would significantly affect the NPV calculation. The breakeven diesel price chart addresses this.

2. **No demand growth:** The model assumes 140 buses throughout the 20-year project life. Fleet expansion or reduction is not modelled.

3. **No learning curve for electricity costs:** The model allows electricity price sensitivity but does not model a declining trajectory (e.g., declining renewable costs over time).

4. **Single carbon price per scenario:** A static carbon price is applied. In reality, UK ETS prices are volatile and expected to rise over time.

5. **100% HRS utilisation:** The cost model assumes stations are always at full capacity. Early-stage low utilisation would worsen the economics.

6. **Grid connection costs for electrolyser expansion:** The 75% BoP factor is intended to capture grid connection costs, but actual costs depend heavily on proximity to HV infrastructure at Tyseley.

---

