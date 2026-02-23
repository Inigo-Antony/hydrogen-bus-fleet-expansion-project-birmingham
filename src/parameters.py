"""
parameters.py
=============
All baseline constants derived from the coursework report:
  "Analysis of Hydrogen Refuelling Infrastructure for Birmingham's Fuel Cell Bus Fleet"
  - Inigo Antony Michael Selvam, MSc Sustainable Energy Systems, University of Birmingham

Units are SI where possible; explicit unit comments are given for every value.
"""

# ──────────────────────────────────────────────
# FLEET
# ──────────────────────────────────────────────
EXISTING_BUSES      = 20          # buses currently operational (Wrightbus StreetDeck Hydroliner)
TOTAL_BUSES         = 140         # full planned fleet size
NEW_BUSES           = TOTAL_BUSES - EXISTING_BUSES   # buses to be added

# ──────────────────────────────────────────────
# VEHICLE SPECIFICATIONS  (Wrightbus StreetDeck Hydroliner FCEV)
# ──────────────────────────────────────────────
TANK_CAPACITY_KG    = 27.0        # kg H2 per bus
TANK_PRESSURE_BAR   = 350         # bar
MAX_RANGE_KM        = 483         # km  (300 miles → 482.8 km)
REFUEL_TIME_MIN     = 8           # minutes for full refuel

# Fuel economy
FUEL_ECONOMY_KG_100KM = 8.5      # kg H2 / 100 km  (report baseline; spec sheet max = 9)

# ──────────────────────────────────────────────
# OPERATIONS
# ──────────────────────────────────────────────
DAILY_MILEAGE_KM    = 300         # km/bus/day  (NXWM operational assumption)
DAYS_PER_YEAR       = 365

# ──────────────────────────────────────────────
# HYDROGEN DEMAND
# ──────────────────────────────────────────────
EXISTING_TYSELEY_CAPACITY_KG_DAY = 1_000   # kg/day  (Hygen Energy, current capacity)

# ──────────────────────────────────────────────
# ELECTROLYSER / PRODUCTION (Tyseley PEM expansion)
# ──────────────────────────────────────────────
EXISTING_ELECTROLYSER_MWE   = 3.0       # MWe already installed
ELECTROLYSER_YIELD          = 267       # kg H2 / day / MWe  (from existing unit performance)
NEW_ELECTROLYSER_MWE        = 12.0      # MWe to be added
ELECTROLYSER_COST_PER_KW    = 750       # £/kW  (2025 large-scale PEM, adapted from $1000/kW)
BOP_FRACTION                = 0.75      # BoP + installation as fraction of equipment cost
ELECTROLYSER_LIFETIME_YR    = 25        # years  (typical PEM design life)
ELECTROLYSER_EFFICIENCY_KWH_KG = 55.0  # kWh_electricity / kg H2  (HHV-based PEM, ~70% efficiency)
STACK_REPLACEMENT_FRACTION  = 0.15     # fraction of CAPEX every ~10 years → annualised ~1.5%/yr
ELECTROLYSER_OPEX_FRAC      = 0.02     # non-energy OPEX as fraction of CAPEX per year

# ──────────────────────────────────────────────
# BASELINE ELECTRICITY PRICE
# ──────────────────────────────────────────────
ELECTRICITY_PRICE_GBP_MWH   = 57.0     # £/MWh  (back-calculated from LCOH = £8.36/kg at baseline)
# Sensitivity sweep range
ELEC_PRICE_MIN_GBP_MWH      = 20.0
ELEC_PRICE_MAX_GBP_MWH      = 120.0

# ──────────────────────────────────────────────
# TRANSPORT (GH2 tube trailer delivery)
# ──────────────────────────────────────────────
TRAILER_PAYLOAD_KG          = 1_000    # kg per delivery (500 bar container trailer)
TRANSPORT_COST_GBP_KG       = 0.85    # £/kg H2  (≈ €1/kg at 1.18 EUR/GBP)

# ──────────────────────────────────────────────
# HRS (Hydrogen Refuelling Station)
# ──────────────────────────────────────────────
HRS_CAPACITY_KG_DAY         = 1_000   # kg/day per satellite station (2-dispenser, medium)
HRS_OPEX_GBP_KG             = 1.04    # £/kg  (≈ €1.22/kg at 1.18 EUR/GBP)
HRS_CAPEX_EUR_PER_STATION   = 2_850_000  # € per station (Thomas et al., 2019)
EUR_GBP                     = 1.18    # exchange rate used throughout report
NEW_HRS_STATIONS            = 3       # Perry Barr, Yardley Wood, Acocks Green

# Dispensing network breakdown (kg/day)
TYSELEY_DISPENSING_CAPACITY = 800
PERRY_BARR_CAPACITY         = 1_000
YARDLEY_WOOD_CAPACITY       = 1_000
ACOCKS_GREEN_CAPACITY       = 800
TOTAL_NETWORK_CAPACITY      = (TYSELEY_DISPENSING_CAPACITY + PERRY_BARR_CAPACITY +
                               YARDLEY_WOOD_CAPACITY + ACOCKS_GREEN_CAPACITY)

# ──────────────────────────────────────────────
# FINANCIAL
# ──────────────────────────────────────────────
DISCOUNT_RATE               = 0.08    # baseline WACC (8%)
PROJECT_LIFE_YR             = 20      # years
OPERATING_HOURS_PER_YR      = 8_000   # hr/yr for electrolyser (91% availability)

# ──────────────────────────────────────────────
# EMISSIONS
# ──────────────────────────────────────────────
GRID_CARBON_INTENSITY_G_KWH = 35.0   # gCO2e/kWh  (offshore wind assumption)
HRS_ENERGY_KWH_KG           = 4.21   # kWh electricity per kg H2 dispensed (compression + cooling)
TRANSPORT_EMISSION_KG_KG    = 0.027  # kg CO2e per kg H2 transported (diesel truck, short urban)

# Diesel baseline
DIESEL_EMISSION_KG_KM       = 0.90   # kg CO2e/km for diesel double-decker bus
DIESEL_PRICE_GBP_LITRE      = 1.40   # £/litre baseline
DIESEL_FUEL_ECONOMY_KM_L    = 300/184.04  # km/litre  (from report Table 5)
DIESEL_TANK_LITRES          = 245     # litres

# Carbon price sensitivity
CARBON_PRICE_BASELINE       = 50      # £/tonne CO2e
CARBON_PRICE_MIN            = 20
CARBON_PRICE_MAX            = 200
