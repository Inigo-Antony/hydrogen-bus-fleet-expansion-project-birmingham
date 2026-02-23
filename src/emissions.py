"""
emissions.py
============
Well-to-Wheel (WtW) CO2 equivalent emission calculations for:
  - Hydrogen pathway (PEM electrolysis + GH2 transport + HRS operations)
  - Diesel baseline (combustion only, WtW scope per DEFRA factors)
"""

from dataclasses import dataclass
from src.parameters import (
    GRID_CARBON_INTENSITY_G_KWH, ELECTROLYSER_EFFICIENCY_KWH_KG,
    HRS_ENERGY_KWH_KG, TRANSPORT_EMISSION_KG_KG,
    DIESEL_EMISSION_KG_KM,
    TOTAL_BUSES, DAILY_MILEAGE_KM, DAYS_PER_YEAR,
)
from src.demand import calculate_demand


@dataclass
class EmissionsResults:
    # H2 pathway emission factors (kg CO2e per kg H2)
    production_co2_kg_kgh2:   float
    hrs_co2_kg_kgh2:          float
    transport_co2_kg_kgh2:    float
    total_h2_ef_kg_kgh2:      float

    # Annual totals
    h2_annual_co2_tonnes:     float
    diesel_annual_co2_tonnes: float
    co2_saving_tonnes_yr:     float
    co2_reduction_pct:        float


def calculate_emissions(
    grid_carbon_intensity: float = GRID_CARBON_INTENSITY_G_KWH,
) -> EmissionsResults:
    """
    Calculate WtW CO2e emissions for both pathways.

    H2 pathway
    ----------
    1. Production:  electrolyser_efficiency (kWh/kg) × grid_intensity (gCO2e/kWh) / 1000
    2. HRS:         hrs_energy (kWh/kg) × grid_intensity / 1000
    3. Transport:   fixed factor from Climatiq (rigid truck diesel, urban distances)

    Diesel pathway
    --------------
    Emission factor per km × annual fleet mileage
    """
    demand = calculate_demand()

    # H2 emission factors
    prod_ef   = (ELECTROLYSER_EFFICIENCY_KWH_KG * grid_carbon_intensity) / 1_000   # kg CO2e/kg H2
    hrs_ef    = (HRS_ENERGY_KWH_KG * grid_carbon_intensity) / 1_000                # kg CO2e/kg H2
    trans_ef  = TRANSPORT_EMISSION_KG_KG                                            # kg CO2e/kg H2
    total_ef  = prod_ef + hrs_ef + trans_ef

    # Annual totals
    h2_annual_co2  = (demand.annual_total_kg * total_ef) / 1_000                   # tonnes
    diesel_annual_co2 = (demand.annual_fleet_mileage_km * DIESEL_EMISSION_KG_KM) / 1_000  # tonnes
    saving = diesel_annual_co2 - h2_annual_co2
    reduction_pct = (saving / diesel_annual_co2) * 100

    return EmissionsResults(
        production_co2_kg_kgh2=round(prod_ef, 4),
        hrs_co2_kg_kgh2=round(hrs_ef, 4),
        transport_co2_kg_kgh2=round(trans_ef, 4),
        total_h2_ef_kg_kgh2=round(total_ef, 4),
        h2_annual_co2_tonnes=round(h2_annual_co2, 1),
        diesel_annual_co2_tonnes=round(diesel_annual_co2, 1),
        co2_saving_tonnes_yr=round(saving, 1),
        co2_reduction_pct=round(reduction_pct, 1),
    )
