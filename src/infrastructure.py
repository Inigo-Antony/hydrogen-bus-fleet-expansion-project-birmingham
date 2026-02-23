"""
infrastructure.py
=================
CAPEX and capacity calculations for:
  - PEM electrolyser expansion at Tyseley Energy Park
  - Hydrogen Refuelling Station (HRS) network (4 stations)
"""

from dataclasses import dataclass
from src.parameters import (
    NEW_ELECTROLYSER_MWE, ELECTROLYSER_COST_PER_KW,
    BOP_FRACTION, EUR_GBP, HRS_CAPEX_EUR_PER_STATION,
    NEW_HRS_STATIONS, ELECTROLYSER_YIELD,
    EXISTING_TYSELEY_CAPACITY_KG_DAY,
    TOTAL_NETWORK_CAPACITY,
)


@dataclass
class InfrastructureCapex:
    # Electrolyser
    electrolyser_equipment_gbp:   float
    electrolyser_bop_gbp:         float
    electrolyser_total_gbp:       float
    # HRS
    hrs_per_station_gbp:          float
    hrs_total_gbp:                float
    # Combined
    total_capex_gbp:              float
    # Production capacity after expansion
    new_production_kg_day:        float
    total_production_kg_day:      float
    total_network_dispensing_kg_day: float


def calculate_capex(
    new_electrolyser_mwe: float = NEW_ELECTROLYSER_MWE,
    electrolyser_cost_per_kw: float = ELECTROLYSER_COST_PER_KW,
    bop_fraction: float = BOP_FRACTION,
    hrs_capex_eur: float = HRS_CAPEX_EUR_PER_STATION,
    n_new_stations: int = NEW_HRS_STATIONS,
    eur_gbp: float = EUR_GBP,
) -> InfrastructureCapex:
    """
    Compute total capital expenditure for the infrastructure expansion.

    Electrolyser
    ------------
    Equipment cost = capacity_kW * £/kW
    BoP & installation = equipment_cost * bop_fraction
    Total electrolyser CAPEX = equipment + BoP

    HRS
    ---
    Per-station cost from Thomas et al. (2019) in EUR, converted to GBP.
    Total = per_station * n_stations
    """
    # Electrolyser
    capacity_kw = new_electrolyser_mwe * 1_000
    equip = capacity_kw * electrolyser_cost_per_kw
    bop   = equip * bop_fraction
    elec_total = equip + bop

    # HRS
    hrs_per_station_gbp = hrs_capex_eur / eur_gbp
    hrs_total = hrs_per_station_gbp * n_new_stations

    total_capex = elec_total + hrs_total

    # Production capacities
    new_prod = new_electrolyser_mwe * ELECTROLYSER_YIELD
    total_prod = EXISTING_TYSELEY_CAPACITY_KG_DAY + new_prod

    return InfrastructureCapex(
        electrolyser_equipment_gbp=round(equip, 0),
        electrolyser_bop_gbp=round(bop, 0),
        electrolyser_total_gbp=round(elec_total, 0),
        hrs_per_station_gbp=round(hrs_per_station_gbp, 0),
        hrs_total_gbp=round(hrs_total, 0),
        total_capex_gbp=round(total_capex, 0),
        new_production_kg_day=round(new_prod, 0),
        total_production_kg_day=round(total_prod, 0),
        total_network_dispensing_kg_day=TOTAL_NETWORK_CAPACITY,
    )
