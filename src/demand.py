"""
demand.py
=========
Calculates hydrogen demand for the Birmingham FCEV bus fleet.
All formulas are explicit and traceable back to the report methodology.
"""

from dataclasses import dataclass
from src.parameters import (
    TOTAL_BUSES, EXISTING_BUSES, FUEL_ECONOMY_KG_100KM,
    DAILY_MILEAGE_KM, DAYS_PER_YEAR, EXISTING_TYSELEY_CAPACITY_KG_DAY
)


@dataclass
class DemandResults:
    daily_per_bus_kg:       float
    existing_fleet_daily_kg: float
    full_fleet_daily_kg:    float
    supply_gap_kg_day:      float
    annual_total_kg:        float
    annual_total_tonnes:    float
    annual_fleet_mileage_km: float


def calculate_demand(
    total_buses:      int   = TOTAL_BUSES,
    fuel_economy:     float = FUEL_ECONOMY_KG_100KM,
    daily_mileage_km: float = DAILY_MILEAGE_KM,
    existing_capacity_kg_day: float = EXISTING_TYSELEY_CAPACITY_KG_DAY,
) -> DemandResults:
    """
    Compute daily and annual hydrogen demand from first principles.

    Parameters
    ----------
    total_buses : int
        Size of the full planned fleet.
    fuel_economy : float
        Hydrogen consumption in kg per 100 km.
    daily_mileage_km : float
        Average daily distance each bus covers.
    existing_capacity_kg_day : float
        Existing production capacity at Tyseley before expansion.

    Returns
    -------
    DemandResults
    """
    daily_per_bus = (daily_mileage_km / 100.0) * fuel_economy          # kg/bus/day
    full_fleet_daily = total_buses * daily_per_bus                      # kg/day
    existing_fleet_daily = EXISTING_BUSES * daily_per_bus              # kg/day
    supply_gap = full_fleet_daily - existing_capacity_kg_day           # kg/day
    annual_total = full_fleet_daily * DAYS_PER_YEAR                    # kg/year
    annual_mileage = total_buses * daily_mileage_km * DAYS_PER_YEAR   # km/year

    return DemandResults(
        daily_per_bus_kg=round(daily_per_bus, 2),
        existing_fleet_daily_kg=round(existing_fleet_daily, 1),
        full_fleet_daily_kg=round(full_fleet_daily, 1),
        supply_gap_kg_day=round(supply_gap, 1),
        annual_total_kg=round(annual_total, 0),
        annual_total_tonnes=round(annual_total / 1_000, 1),
        annual_fleet_mileage_km=round(annual_mileage, 0),
    )
