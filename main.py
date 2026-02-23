"""
main.py
=======
Entry point for the Birmingham H2 Bus Fleet Techno-Economic Analysis.

Usage
-----
    python main.py

Outputs
-------
- Console summary table of all key metrics
- 9 publication-quality PNG figures in ./outputs/
"""

from src.demand import calculate_demand
from src.infrastructure import calculate_capex
from src.economics import calculate_lcoh, calculate_annual_costs, calculate_npv_irr
from src.emissions import calculate_emissions
from src.sensitivity import generate_all_figures
from src.parameters import ELECTRICITY_PRICE_GBP_MWH, CARBON_PRICE_BASELINE, DISCOUNT_RATE


def print_section(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


def run_analysis():
    print("=" * 60)
    print("  Birmingham H2 Bus Fleet – Techno-Economic Analysis")
    print("  Inigo Antony Michael Selvam | MSc Sustainable Energy Systems")
    print("=" * 60)

    # ── Demand ────────────────────────────────────────────────
    print_section("1. HYDROGEN DEMAND")
    d = calculate_demand()
    print(f"  Daily consumption per bus       : {d.daily_per_bus_kg:.1f}  kg/bus/day")
    print(f"  Existing fleet (20 buses)        : {d.existing_fleet_daily_kg:.0f}  kg/day")
    print(f"  Full fleet (140 buses)           : {d.full_fleet_daily_kg:.0f}  kg/day")
    print(f"  Supply gap to cover              : {d.supply_gap_kg_day:.0f}  kg/day")
    print(f"  Annual demand                    : {d.annual_total_tonnes:.0f}  tonnes/yr")
    print(f"  Annual fleet mileage             : {d.annual_fleet_mileage_km:,.0f}  km/yr")

    # ── Infrastructure ────────────────────────────────────────
    print_section("2. INFRASTRUCTURE & CAPEX")
    cap = calculate_capex()
    print(f"  New electrolyser capacity        : 12 MWe  →  {cap.new_production_kg_day:.0f} kg/day")
    print(f"  Total network production         : {cap.total_production_kg_day:.0f}  kg/day")
    print(f"  Network dispensing capacity      : {cap.total_network_dispensing_kg_day}  kg/day")
    print(f"  Electrolyser equipment           : £{cap.electrolyser_equipment_gbp/1e6:.2f}M")
    print(f"  BoP & installation               : £{cap.electrolyser_bop_gbp/1e6:.2f}M")
    print(f"  Electrolyser CAPEX total         : £{cap.electrolyser_total_gbp/1e6:.2f}M")
    print(f"  3 × HRS stations                 : £{cap.hrs_total_gbp/1e6:.2f}M")
    print(f"  TOTAL CAPEX                      : £{cap.total_capex_gbp/1e6:.2f}M")

    # ── LCOH ─────────────────────────────────────────────────
    print_section("3. LEVELISED COST OF HYDROGEN")
    lc = calculate_lcoh(ELECTRICITY_PRICE_GBP_MWH)
    print(f"  Electricity price assumption     : £{ELECTRICITY_PRICE_GBP_MWH:.0f}/MWh")
    print(f"  Electricity cost component       : £{lc.electricity_cost_gbp_kg:.3f}/kg")
    print(f"  CAPEX amortised                  : £{lc.capex_amortised_gbp_kg:.3f}/kg")
    print(f"  Non-energy OPEX                  : £{lc.opex_non_energy_gbp_kg:.3f}/kg")
    print(f"  Stack replacement                : £{lc.stack_replacement_gbp_kg:.3f}/kg")
    print(f"  Production LCOH                  : £{lc.production_lcoh_gbp_kg:.3f}/kg")
    print(f"  Transport                        : £{lc.transport_gbp_kg:.3f}/kg")
    print(f"  HRS operations                   : £{lc.hrs_opex_gbp_kg:.3f}/kg")
    print(f"  ┌─ TOTAL DISPENSED COST         : £{lc.total_dispensed_cost_gbp_kg:.2f}/kg ─┐")

    # ── Annual costs ─────────────────────────────────────────
    print_section("4. ANNUAL FLEET OPERATING COSTS")
    ac = calculate_annual_costs(ELECTRICITY_PRICE_GBP_MWH, CARBON_PRICE_BASELINE)
    print(f"  H2 fleet annual fuel cost        : £{ac.h2_fuel_cost_gbp/1e6:.2f}M")
    print(f"  Diesel fleet annual fuel cost    : £{ac.diesel_fuel_cost_gbp/1e6:.2f}M")
    print(f"  Fuel cost saving (H2 vs diesel)  : £{ac.fuel_saving_gbp/1e6:.2f}M/yr")
    print(f"  CO₂ saved (@ £{CARBON_PRICE_BASELINE}/t)          : £{ac.carbon_saving_value_gbp/1e6:.2f}M/yr")
    print(f"  Total annual benefit             : £{ac.total_annual_benefit_gbp/1e6:.2f}M/yr")

    # ── Emissions ────────────────────────────────────────────
    print_section("5. WELL-TO-WHEEL CO₂ ANALYSIS")
    em = calculate_emissions()
    print(f"  H2 emission factor               : {em.total_h2_ef_kg_kgh2:.3f}  kg CO₂e/kg H2")
    print(f"    of which: production           : {em.production_co2_kg_kgh2:.3f}")
    print(f"             HRS operations        : {em.hrs_co2_kg_kgh2:.4f}")
    print(f"             transport             : {em.transport_co2_kg_kgh2:.3f}")
    print(f"  H2 fleet annual CO₂              : {em.h2_annual_co2_tonnes:,.0f}  t/yr")
    print(f"  Diesel fleet annual CO₂          : {em.diesel_annual_co2_tonnes:,.0f}  t/yr")
    print(f"  Annual CO₂ saving                : {em.co2_saving_tonnes_yr:,.0f}  t/yr")
    print(f"  CO₂ reduction                    : {em.co2_reduction_pct:.1f}%")

    # ── NPV / IRR ────────────────────────────────────────────
    print_section("6. FINANCIAL ANALYSIS  (NPV / IRR)")
    fin = calculate_npv_irr(ELECTRICITY_PRICE_GBP_MWH, CARBON_PRICE_BASELINE, DISCOUNT_RATE)
    print(f"  Discount rate (WACC)             : {DISCOUNT_RATE*100:.0f}%")
    print(f"  Project life                     : 20 years")
    print(f"  Total CAPEX                      : £{fin.total_capex_gbp/1e6:.2f}M")
    print(f"  Annual benefit (fuel + carbon)   : £{fin.annual_benefit_gbp/1e6:.2f}M/yr")
    print(f"  NPV                              : £{fin.npv_gbp/1e6:.2f}M")
    if fin.irr_pct is not None:
        print(f"  IRR                              : {fin.irr_pct:.1f}%")
    else:
        print("  IRR                              : not found (negative benefit)")
    print(f"  Simple payback                   : {fin.simple_payback_yr:.1f}  years")
    print(f"  Benefit-cost ratio               : {fin.benefit_cost_ratio:.3f}")

    # ── Figures ──────────────────────────────────────────────
    print_section("7. GENERATING FIGURES")
    generate_all_figures()
    print("\n  ✓ Analysis complete.")


if __name__ == "__main__":
    run_analysis()
