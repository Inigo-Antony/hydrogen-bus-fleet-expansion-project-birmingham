"""
economics.py
============
Levelised Cost of Hydrogen (LCOH), annual operating costs,
NPV and IRR for the infrastructure investment.

Benefit streams for NPV:
  1. Fuel cost savings (diesel fuel cost avoided vs. H2 fuel cost)
  2. Carbon cost avoided (CO2e savings × carbon price)
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from src.parameters import (
    ELECTRICITY_PRICE_GBP_MWH, ELECTROLYSER_EFFICIENCY_KWH_KG,
    ELECTROLYSER_LIFETIME_YR, NEW_ELECTROLYSER_MWE, ELECTROLYSER_YIELD,
    DISCOUNT_RATE, PROJECT_LIFE_YR,
    TRANSPORT_COST_GBP_KG, HRS_OPEX_GBP_KG,
    DIESEL_PRICE_GBP_LITRE, DIESEL_FUEL_ECONOMY_KM_L,
    DAILY_MILEAGE_KM, TOTAL_BUSES, DAYS_PER_YEAR,
    ELECTROLYSER_OPEX_FRAC, STACK_REPLACEMENT_FRACTION,
    OPERATING_HOURS_PER_YR, CARBON_PRICE_BASELINE,
    ELECTROLYSER_COST_PER_KW, BOP_FRACTION,
)
from src.demand import calculate_demand
from src.infrastructure import calculate_capex
from src.emissions import calculate_emissions


# ── helpers ──────────────────────────────────────────────────────────────────

def _annuity_factor(rate: float, n_years: int) -> float:
    """Capital recovery factor (annuity factor) for given WACC and project life."""
    if rate == 0:
        return n_years
    return (rate * (1 + rate) ** n_years) / ((1 + rate) ** n_years - 1)


def _npv(cash_flows: np.ndarray, discount_rate: float) -> float:
    """Net present value of a cash-flow array (index 0 = year 0 = CAPEX outlay)."""
    t = np.arange(len(cash_flows))
    return float(np.sum(cash_flows / (1 + discount_rate) ** t))


def _irr(cash_flows: np.ndarray) -> Optional[float]:
    """
    Internal rate of return via bisection on NPV(r) = 0.
    Searches in the range [-50%, +200%] which covers all practical project IRRs.
    Returns None if no sign change found in that range (project never breaks even).
    """
    def npv_at_rate(r):
        t = np.arange(len(cash_flows))
        return float(np.sum(cash_flows / (1 + r) ** t))

    # Check for sign change (necessary for IRR to exist)
    lo, hi = -0.5, 2.0
    npv_lo = npv_at_rate(lo)
    npv_hi = npv_at_rate(hi)
    if npv_lo * npv_hi > 0:
        return None  # no sign change → no real IRR in range

    # Bisection
    for _ in range(100):
        mid = (lo + hi) / 2
        npv_mid = npv_at_rate(mid)
        if abs(npv_mid) < 1.0:  # converged to within £1
            return mid
        if npv_lo * npv_mid < 0:
            hi = mid
        else:
            lo = mid
            npv_lo = npv_mid
    return (lo + hi) / 2


# ── main functions ────────────────────────────────────────────────────────────

@dataclass
class LCOHBreakdown:
    electricity_cost_gbp_kg:   float
    capex_amortised_gbp_kg:    float
    opex_non_energy_gbp_kg:    float
    stack_replacement_gbp_kg:  float
    production_lcoh_gbp_kg:    float
    transport_gbp_kg:          float
    hrs_opex_gbp_kg:           float
    total_dispensed_cost_gbp_kg: float


def calculate_lcoh(
    electricity_price_gbp_mwh:  float = ELECTRICITY_PRICE_GBP_MWH,
    discount_rate:               float = DISCOUNT_RATE,
    # Explicit overrides for sensitivity / tornado analysis.
    # When None, the value from parameters.py is used.
    electrolyser_efficiency_kwh_kg: Optional[float] = None,
    electrolyser_cost_per_kw:       Optional[float] = None,
    bop_fraction:                   Optional[float] = None,
    transport_cost_gbp_kg:          Optional[float] = None,
    hrs_opex_gbp_kg_override:       Optional[float] = None,
) -> LCOHBreakdown:
    """
    Levelised Cost of Hydrogen at the dispenser (£/kg).

    Production LCOH components
    --------------------------
    1. Electricity:    kWh/kg × £/kWh
    2. CAPEX amortised: annual_capex / annual_production
    3. Non-energy OPEX: opex_frac × CAPEX / annual_production
    4. Stack replacement: stack_frac × CAPEX / annual_production

    All parameters default to the values in parameters.py. Pass explicit values
    to override individual parameters for sensitivity analysis — this avoids the
    Python "from ... import" local-binding issue that breaks monkey-patching.
    """
    # Resolve effective parameter values
    eff      = electrolyser_efficiency_kwh_kg if electrolyser_efficiency_kwh_kg is not None else ELECTROLYSER_EFFICIENCY_KWH_KG
    cost_kw  = electrolyser_cost_per_kw       if electrolyser_cost_per_kw       is not None else ELECTROLYSER_COST_PER_KW
    bop_frac = bop_fraction                   if bop_fraction                   is not None else BOP_FRACTION
    trans    = transport_cost_gbp_kg          if transport_cost_gbp_kg          is not None else TRANSPORT_COST_GBP_KG
    hrs_opex = hrs_opex_gbp_kg_override       if hrs_opex_gbp_kg_override       is not None else HRS_OPEX_GBP_KG

    # Recalculate electrolyser CAPEX with potentially overridden cost/kW and BoP fraction
    from src.infrastructure import calculate_capex
    capex = calculate_capex(
        electrolyser_cost_per_kw=cost_kw,
        bop_fraction=bop_frac,
    )

    # Annual H2 production from new electrolyser
    annual_prod_kg = NEW_ELECTROLYSER_MWE * ELECTROLYSER_YIELD * DAYS_PER_YEAR

    # 1. Electricity cost
    elec_gbp_kwh    = electricity_price_gbp_mwh / 1_000
    electricity_cost = eff * elec_gbp_kwh                                       # £/kg

    # 2. CAPEX amortised using capital recovery factor
    crf = _annuity_factor(discount_rate, ELECTROLYSER_LIFETIME_YR)
    annual_capex_charge = capex.electrolyser_total_gbp * crf
    capex_per_kg = annual_capex_charge / annual_prod_kg                         # £/kg

    # 3. Non-energy OPEX
    annual_opex = capex.electrolyser_total_gbp * ELECTROLYSER_OPEX_FRAC
    opex_per_kg = annual_opex / annual_prod_kg                                  # £/kg

    # 4. Stack replacement (annualised)
    annual_stack = capex.electrolyser_total_gbp * (STACK_REPLACEMENT_FRACTION / 10)
    stack_per_kg = annual_stack / annual_prod_kg                                # £/kg

    production_lcoh = electricity_cost + capex_per_kg + opex_per_kg + stack_per_kg
    total_cost      = production_lcoh + trans + hrs_opex

    return LCOHBreakdown(
        electricity_cost_gbp_kg=round(electricity_cost, 3),
        capex_amortised_gbp_kg=round(capex_per_kg, 3),
        opex_non_energy_gbp_kg=round(opex_per_kg, 3),
        stack_replacement_gbp_kg=round(stack_per_kg, 3),
        production_lcoh_gbp_kg=round(production_lcoh, 3),
        transport_gbp_kg=round(trans, 3),
        hrs_opex_gbp_kg=round(hrs_opex, 3),
        total_dispensed_cost_gbp_kg=round(total_cost, 3),
    )


@dataclass
class AnnualCosts:
    h2_fuel_cost_gbp:     float
    diesel_fuel_cost_gbp: float
    fuel_saving_gbp:      float
    carbon_saving_tonnes: float
    carbon_saving_value_gbp: float
    total_annual_benefit_gbp: float


def calculate_annual_costs(
    electricity_price_gbp_mwh: float = ELECTRICITY_PRICE_GBP_MWH,
    carbon_price_gbp_tonne: float = CARBON_PRICE_BASELINE,
    diesel_price_gbp_litre: float = DIESEL_PRICE_GBP_LITRE,
) -> AnnualCosts:
    """
    Compare annual fuel costs (H2 vs diesel) and carbon cost savings.
    """
    demand  = calculate_demand()
    lcoh    = calculate_lcoh(electricity_price_gbp_mwh)
    emis    = calculate_emissions(electricity_price_gbp_mwh)

    # H2 total annual fuel cost
    h2_cost = demand.annual_total_kg * lcoh.total_dispensed_cost_gbp_kg

    # Diesel equivalent annual fuel cost
    total_diesel_litres = (TOTAL_BUSES * DAILY_MILEAGE_KM * DAYS_PER_YEAR) / DIESEL_FUEL_ECONOMY_KM_L
    diesel_cost = total_diesel_litres * diesel_price_gbp_litre

    fuel_saving = diesel_cost - h2_cost

    # Carbon cost saved
    co2_saved = emis.co2_saving_tonnes_yr
    carbon_value = co2_saved * carbon_price_gbp_tonne

    total_benefit = fuel_saving + carbon_value

    return AnnualCosts(
        h2_fuel_cost_gbp=round(h2_cost, 0),
        diesel_fuel_cost_gbp=round(diesel_cost, 0),
        fuel_saving_gbp=round(fuel_saving, 0),
        carbon_saving_tonnes=round(co2_saved, 1),
        carbon_saving_value_gbp=round(carbon_value, 0),
        total_annual_benefit_gbp=round(total_benefit, 0),
    )


@dataclass
class FinancialAnalysis:
    total_capex_gbp:       float
    annual_benefit_gbp:    float
    npv_gbp:               float
    irr_pct:               Optional[float]
    simple_payback_yr:     float
    benefit_cost_ratio:    float


def calculate_npv_irr(
    electricity_price_gbp_mwh: float = ELECTRICITY_PRICE_GBP_MWH,
    carbon_price_gbp_tonne: float = CARBON_PRICE_BASELINE,
    discount_rate: float = DISCOUNT_RATE,
    project_life_yr: int = PROJECT_LIFE_YR,
    diesel_price_gbp_litre: float = DIESEL_PRICE_GBP_LITRE,
) -> FinancialAnalysis:
    """
    NPV and IRR for the £24M+ infrastructure investment.

    Cash flow structure
    -------------------
    Year 0  : -CAPEX (full outlay)
    Year 1-N: + annual benefit (fuel savings + carbon savings)

    Annual benefits increase slightly with inflation but we use real (inflation-adjusted)
    cash flows at a real discount rate for simplicity.
    """
    capex = calculate_capex()
    costs = calculate_annual_costs(
        electricity_price_gbp_mwh, carbon_price_gbp_tonne, diesel_price_gbp_litre
    )

    total_capex = capex.total_capex_gbp
    annual_benefit = costs.total_annual_benefit_gbp

    # Build cash flow array: [year0, year1, ..., yearN]
    cash_flows = np.array([-total_capex] + [annual_benefit] * project_life_yr)

    npv = _npv(cash_flows, discount_rate)
    irr_val = _irr(cash_flows)
    irr_pct = round(irr_val * 100, 2) if irr_val is not None else None

    simple_payback = total_capex / annual_benefit if annual_benefit > 0 else float("inf")

    # Benefit-cost ratio: PV of benefits / CAPEX
    pv_benefits = annual_benefit * ((1 - (1 + discount_rate) ** -project_life_yr) / discount_rate)
    bcr = pv_benefits / total_capex

    return FinancialAnalysis(
        total_capex_gbp=round(total_capex, 0),
        annual_benefit_gbp=round(annual_benefit, 0),
        npv_gbp=round(npv, 0),
        irr_pct=irr_pct,
        simple_payback_yr=round(simple_payback, 1),
        benefit_cost_ratio=round(bcr, 3),
    )


def diesel_breakeven_price(
    electricity_price_gbp_mwh: float,
    carbon_price_gbp_tonne: float = 0.0,
) -> float:
    """
    Returns the diesel price (£/litre) at which annual H2 fuel cost equals annual diesel cost.
    Optionally includes a carbon price on diesel emissions.

    diesel_cost = h2_cost  →  solve for diesel_price_per_litre
    """
    demand = calculate_demand()
    lcoh   = calculate_lcoh(electricity_price_gbp_mwh)
    emis   = calculate_emissions(electricity_price_gbp_mwh)

    h2_annual = demand.annual_total_kg * lcoh.total_dispensed_cost_gbp_kg
    # Carbon penalty on diesel
    diesel_carbon_penalty = (emis.diesel_annual_co2_tonnes * carbon_price_gbp_tonne)
    total_diesel_litres = (TOTAL_BUSES * DAILY_MILEAGE_KM * DAYS_PER_YEAR) / DIESEL_FUEL_ECONOMY_KM_L

    # (total_litres × price + carbon_penalty) = h2_annual
    breakeven = (h2_annual - diesel_carbon_penalty) / total_diesel_litres
    return round(breakeven, 3)
