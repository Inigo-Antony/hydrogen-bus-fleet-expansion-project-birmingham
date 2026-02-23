"""
sensitivity.py
==============
Generates all sensitivity analyses and saves publication-quality matplotlib figures.

Figures produced
----------------
1.  lcoh_vs_electricity.png     – LCOH components stacked bar + total line vs electricity price
2.  annual_cost_vs_elec.png     – H2 vs diesel annual fleet fuel cost vs electricity price
3.  breakeven_diesel.png        – Breakeven diesel price vs electricity price (multiple carbon prices)
4.  npv_vs_elec_carbon.png      – NPV vs electricity price for multiple carbon price scenarios
5.  irr_vs_elec.png             – IRR vs electricity price for multiple carbon prices
6.  npv_heatmap.png             – NPV heatmap: electricity price × carbon price
7.  emissions_comparison.png    – WtW emissions bar chart (H2 vs diesel) + breakdown
8.  capex_breakdown.png         – CAPEX waterfall / stacked bar
9.  lcoh_sensitivity_tornado.png– Tornado chart: one-at-a-time parameter sensitivity on LCOH
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import TwoSlopeNorm

from src.parameters import (
    ELEC_PRICE_MIN_GBP_MWH, ELEC_PRICE_MAX_GBP_MWH,
    CARBON_PRICE_MIN, CARBON_PRICE_MAX,
    ELECTRICITY_PRICE_GBP_MWH, CARBON_PRICE_BASELINE,
    DISCOUNT_RATE, PROJECT_LIFE_YR, DIESEL_PRICE_GBP_LITRE,
    TRANSPORT_COST_GBP_KG, HRS_OPEX_GBP_KG,
    ELECTROLYSER_EFFICIENCY_KWH_KG, ELECTROLYSER_COST_PER_KW,
    BOP_FRACTION,
)
from src.economics import (
    calculate_lcoh, calculate_annual_costs, calculate_npv_irr, diesel_breakeven_price
)
from src.infrastructure import calculate_capex
from src.emissions import calculate_emissions

OUTPUT_DIR = "outputs"

# ── style ──────────────────────────────────────────────────────────────────────

PALETTE = {
    "blue":     "#1A6CA8",
    "orange":   "#E07B39",
    "green":    "#2E8B57",
    "red":      "#C0392B",
    "purple":   "#7D3C98",
    "grey":     "#7F8C8D",
    "light_blue": "#AED6F1",
    "light_orange": "#FAD7A0",
}

def _set_style():
    plt.rcParams.update({
        "figure.dpi":        150,
        "figure.facecolor":  "white",
        "axes.facecolor":    "#F8F9FA",
        "axes.grid":         True,
        "axes.grid.which":   "major",
        "grid.color":        "#DDDDDD",
        "grid.linewidth":    0.7,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "font.family":       "sans-serif",
        "font.size":         11,
        "axes.labelsize":    12,
        "axes.titlesize":    13,
        "axes.titleweight":  "bold",
        "legend.frameon":    True,
        "legend.framealpha": 0.9,
    })

def _savefig(fig, name: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Saved {path}")


# ── Figure 1: LCOH vs Electricity Price ───────────────────────────────────────

def plot_lcoh_vs_electricity(elec_range=None):
    if elec_range is None:
        elec_range = np.linspace(ELEC_PRICE_MIN_GBP_MWH, ELEC_PRICE_MAX_GBP_MWH, 80)

    elec_costs, capex_costs, opex_costs, stack_costs, trans_costs, hrs_costs, totals = (
        [], [], [], [], [], [], []
    )
    for ep in elec_range:
        lc = calculate_lcoh(ep)
        elec_costs.append(lc.electricity_cost_gbp_kg)
        capex_costs.append(lc.capex_amortised_gbp_kg)
        opex_costs.append(lc.opex_non_energy_gbp_kg)
        stack_costs.append(lc.stack_replacement_gbp_kg)
        trans_costs.append(lc.transport_gbp_kg)
        hrs_costs.append(lc.hrs_opex_gbp_kg)
        totals.append(lc.total_dispensed_cost_gbp_kg)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bottom = np.zeros(len(elec_range))
    layers = [
        ("Electricity",       elec_costs,  PALETTE["blue"]),
        ("CAPEX (amort.)",    capex_costs, PALETTE["orange"]),
        ("Non-energy OPEX",   opex_costs,  PALETTE["green"]),
        ("Stack replacement", stack_costs, PALETTE["purple"]),
        ("Transport",         trans_costs, PALETTE["grey"]),
        ("HRS operations",    hrs_costs,   PALETTE["red"]),
    ]
    for label, values, colour in layers:
        ax.bar(elec_range, values, bottom=bottom, width=1.1,
               label=label, color=colour, alpha=0.85, linewidth=0)
        bottom += np.array(values)

    ax.plot(elec_range, totals, color="black", lw=2.0, zorder=5, label="Total LCOH")

    # Mark baseline
    baseline_lcoh = calculate_lcoh(ELECTRICITY_PRICE_GBP_MWH)
    ax.axvline(ELECTRICITY_PRICE_GBP_MWH, color="black", ls="--", lw=1.2, alpha=0.6)
    ax.annotate(f"Baseline\n£{ELECTRICITY_PRICE_GBP_MWH}/MWh",
                xy=(ELECTRICITY_PRICE_GBP_MWH, baseline_lcoh.total_dispensed_cost_gbp_kg + 0.3),
                fontsize=9, ha="center", color="black")

    ax.set_xlabel("Electricity Price  (£/MWh)")
    ax.set_ylabel("Cost  (£/kg H₂)")
    ax.set_title("Levelised Cost of Hydrogen at Dispenser vs. Electricity Price")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_xlim(elec_range[0], elec_range[-1])
    ax.set_ylim(0, max(totals) * 1.12)
    fig.tight_layout()
    _savefig(fig, "lcoh_vs_electricity.png")


# ── Figure 2: Annual Fleet Fuel Cost ──────────────────────────────────────────

def plot_annual_cost_vs_electricity(elec_range=None):
    if elec_range is None:
        elec_range = np.linspace(ELEC_PRICE_MIN_GBP_MWH, ELEC_PRICE_MAX_GBP_MWH, 80)

    h2_costs, diesel_costs = [], []
    for ep in elec_range:
        ac = calculate_annual_costs(ep)
        h2_costs.append(ac.h2_fuel_cost_gbp / 1e6)
        diesel_costs.append(ac.diesel_fuel_cost_gbp / 1e6)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(elec_range, h2_costs, color=PALETTE["blue"], lw=2.5, label="H₂ fleet (total fuel cost)")
    ax.axhline(diesel_costs[0], color=PALETTE["orange"], lw=2.5, ls="--",
               label=f"Diesel fleet (£{DIESEL_PRICE_GBP_LITRE}/L baseline)")

    # Fill region
    h2_arr = np.array(h2_costs)
    d_val = diesel_costs[0]
    ax.fill_between(elec_range, h2_arr, d_val,
                    where=(h2_arr < d_val), alpha=0.15, color=PALETTE["green"],
                    label="H₂ cheaper")
    ax.fill_between(elec_range, h2_arr, d_val,
                    where=(h2_arr >= d_val), alpha=0.15, color=PALETTE["red"],
                    label="Diesel cheaper")

    ax.axvline(ELECTRICITY_PRICE_GBP_MWH, color="grey", ls=":", lw=1.3)
    ax.set_xlabel("Electricity Price  (£/MWh)")
    ax.set_ylabel("Annual Fuel Cost  (£M)")
    ax.set_title("Annual Fleet Fuel Cost: Hydrogen vs. Diesel  (140-bus fleet)")
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("£%.1fM"))
    ax.set_xlim(elec_range[0], elec_range[-1])
    fig.tight_layout()
    _savefig(fig, "annual_cost_vs_elec.png")


# ── Figure 3: Breakeven Diesel Price ──────────────────────────────────────────

def plot_breakeven_diesel(elec_range=None):
    if elec_range is None:
        elec_range = np.linspace(ELEC_PRICE_MIN_GBP_MWH, ELEC_PRICE_MAX_GBP_MWH, 100)

    carbon_scenarios = [0, 50, 100, 150]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    colours = [PALETTE["blue"], PALETTE["green"], PALETTE["orange"], PALETTE["red"]]

    for cp, col in zip(carbon_scenarios, colours):
        breakevens = [diesel_breakeven_price(ep, cp) for ep in elec_range]
        ax.plot(elec_range, breakevens, lw=2.2, color=col,
                label=f"Carbon price = £{cp}/t CO₂e")

    # Reference lines
    ax.axhline(DIESEL_PRICE_GBP_LITRE, color="black", ls="--", lw=1.5, alpha=0.7,
               label=f"Current diesel  £{DIESEL_PRICE_GBP_LITRE}/L")
    ax.axhline(2.0, color="grey", ls=":", lw=1.2, alpha=0.6,
               label="Stressed diesel £2.00/L")
    ax.axvline(ELECTRICITY_PRICE_GBP_MWH, color="grey", ls=":", lw=1.3, alpha=0.5)

    ax.set_xlabel("Electricity Price  (£/MWh)")
    ax.set_ylabel("Breakeven Diesel Price  (£/litre)")
    ax.set_title("Diesel Breakeven Price for H₂ Fleet Cost Parity")
    ax.legend(fontsize=9)
    ax.set_xlim(elec_range[0], elec_range[-1])
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    _savefig(fig, "breakeven_diesel.png")


# ── Figure 4: NPV vs Electricity Price ────────────────────────────────────────

def plot_npv_vs_electricity(elec_range=None):
    if elec_range is None:
        elec_range = np.linspace(ELEC_PRICE_MIN_GBP_MWH, ELEC_PRICE_MAX_GBP_MWH, 80)

    carbon_scenarios = [0, 50, 100, 150, 200]
    colours = [PALETTE["grey"], PALETTE["blue"], PALETTE["green"],
               PALETTE["orange"], PALETTE["red"]]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for cp, col in zip(carbon_scenarios, colours):
        npvs = [calculate_npv_irr(ep, cp).npv_gbp / 1e6 for ep in elec_range]
        ax.plot(elec_range, npvs, lw=2.2, color=col,
                label=f"Carbon = £{cp}/t CO₂e")

    ax.axhline(0, color="black", lw=1.5, ls="-")
    ax.axvline(ELECTRICITY_PRICE_GBP_MWH, color="grey", ls=":", lw=1.3)
    ax.fill_between(elec_range,
                    [calculate_npv_irr(ep, CARBON_PRICE_BASELINE).npv_gbp / 1e6
                     for ep in elec_range],
                    0, alpha=0.06, color=PALETTE["blue"])

    ax.set_xlabel("Electricity Price  (£/MWh)")
    ax.set_ylabel("NPV  (£M)")
    ax.set_title(f"NPV of Infrastructure Investment  (20yr, {DISCOUNT_RATE*100:.0f}% discount rate)")
    ax.legend(fontsize=9, title="Carbon price")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("£%.0fM"))
    ax.set_xlim(elec_range[0], elec_range[-1])
    fig.tight_layout()
    _savefig(fig, "npv_vs_elec_carbon.png")


# ── Figure 5: IRR vs Electricity Price ────────────────────────────────────────

def plot_irr_vs_electricity(elec_range=None):
    if elec_range is None:
        elec_range = np.linspace(ELEC_PRICE_MIN_GBP_MWH, ELEC_PRICE_MAX_GBP_MWH, 80)

    carbon_scenarios = [0, 50, 100, 150]
    colours = [PALETTE["grey"], PALETTE["blue"], PALETTE["orange"], PALETTE["red"]]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for cp, col in zip(carbon_scenarios, colours):
        irrs = []
        for ep in elec_range:
            res = calculate_npv_irr(ep, cp)
            irrs.append(res.irr_pct if res.irr_pct is not None else np.nan)
        ax.plot(elec_range, irrs, lw=2.2, color=col,
                label=f"Carbon = £{cp}/t CO₂e")

    ax.axhline(DISCOUNT_RATE * 100, color="black", ls="--", lw=1.5,
               label=f"WACC = {DISCOUNT_RATE*100:.0f}% (hurdle rate)")
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(ELECTRICITY_PRICE_GBP_MWH, color="grey", ls=":", lw=1.3)

    ax.set_xlabel("Electricity Price  (£/MWh)")
    ax.set_ylabel("IRR  (%)")
    ax.set_title("Internal Rate of Return vs. Electricity Price")
    ax.legend(fontsize=9)
    ax.set_xlim(elec_range[0], elec_range[-1])
    fig.tight_layout()
    _savefig(fig, "irr_vs_elec.png")


# ── Figure 6: NPV Heatmap ─────────────────────────────────────────────────────

def plot_npv_heatmap():
    elec_range   = np.linspace(ELEC_PRICE_MIN_GBP_MWH, ELEC_PRICE_MAX_GBP_MWH, 50)
    carbon_range = np.linspace(CARBON_PRICE_MIN, CARBON_PRICE_MAX, 50)

    Z = np.zeros((len(carbon_range), len(elec_range)))
    for i, cp in enumerate(carbon_range):
        for j, ep in enumerate(elec_range):
            Z[i, j] = calculate_npv_irr(ep, cp).npv_gbp / 1e6

    fig, ax = plt.subplots(figsize=(9, 6))
    norm = TwoSlopeNorm(vmin=Z.min(), vcenter=0, vmax=Z.max())
    im = ax.contourf(elec_range, carbon_range, Z, levels=25, cmap="RdYlGn", norm=norm)
    ax.contour(elec_range, carbon_range, Z, levels=[0], colors="black", linewidths=2.0)
    cbar = fig.colorbar(im, ax=ax, label="NPV  (£M)")

    ax.scatter([ELECTRICITY_PRICE_GBP_MWH], [CARBON_PRICE_BASELINE],
               color="white", s=80, zorder=5, edgecolors="black", linewidths=1.5,
               label=f"Baseline  (£{ELECTRICITY_PRICE_GBP_MWH}/MWh, £{CARBON_PRICE_BASELINE}/t)")

    ax.set_xlabel("Electricity Price  (£/MWh)")
    ax.set_ylabel("Carbon Price  (£/t CO₂e)")
    ax.set_title("NPV Heatmap: Electricity Price × Carbon Price\n(Black contour = NPV breakeven)")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    _savefig(fig, "npv_heatmap.png")


# ── Figure 7: Emissions Comparison ────────────────────────────────────────────

def plot_emissions_comparison():
    emis = calculate_emissions()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))

    # Left: annual totals bar
    ax = axes[0]
    categories = ["Diesel\nbaseline", "H₂ fleet\n(offshore wind)"]
    values = [emis.diesel_annual_co2_tonnes, emis.h2_annual_co2_tonnes]
    colours = [PALETTE["orange"], PALETTE["blue"]]
    bars = ax.bar(categories, values, color=colours, width=0.45, zorder=3)
    ax.bar_label(bars, fmt="%.0f t", padding=5, fontsize=11, fontweight="bold")
    ax.annotate(f"−{emis.co2_reduction_pct:.0f}%\n({emis.co2_saving_tonnes_yr:,.0f} t CO₂e saved)",
                xy=(0.5, (emis.diesel_annual_co2_tonnes + emis.h2_annual_co2_tonnes) / 2),
                xytext=(0.5, emis.diesel_annual_co2_tonnes * 0.6),
                ha="center", fontsize=11, color=PALETTE["green"],
                fontweight="bold")
    ax.set_ylabel("Annual CO₂e Emissions  (tonnes/yr)")
    ax.set_title("WtW Annual Emissions Comparison")
    ax.set_ylim(0, emis.diesel_annual_co2_tonnes * 1.18)
    ax.grid(axis="x", visible=False)

    # Right: H2 emission factor breakdown
    ax2 = axes[1]
    components = ["Production\n(electrolysis)", "HRS\n(compression)", "Transport\n(truck)"]
    ef_values = [
        emis.production_co2_kg_kgh2,
        emis.hrs_co2_kg_kgh2,
        emis.transport_co2_kg_kgh2,
    ]
    colours2 = [PALETTE["blue"], PALETTE["purple"], PALETTE["grey"]]
    bars2 = ax2.barh(components, ef_values, color=colours2, height=0.45, zorder=3)
    ax2.bar_label(bars2, fmt="%.3f kg", padding=4, fontsize=10)
    ax2.set_xlabel("Emission Factor  (kg CO₂e / kg H₂)")
    ax2.set_title("H₂ Pathway Emission Factor Breakdown")
    ax2.set_xlim(0, max(ef_values) * 1.3)
    ax2.grid(axis="y", visible=False)

    fig.tight_layout()
    _savefig(fig, "emissions_comparison.png")


# ── Figure 8: CAPEX Breakdown ─────────────────────────────────────────────────

def plot_capex_breakdown():
    cap = calculate_capex()

    fig, ax = plt.subplots(figsize=(9, 5.5))
    components = [
        "Electrolyser\nequipment",
        "BoP &\ninstallation",
        "HRS network\n(3 stations)",
    ]
    values = [
        cap.electrolyser_equipment_gbp / 1e6,
        cap.electrolyser_bop_gbp / 1e6,
        cap.hrs_total_gbp / 1e6,
    ]
    colours = [PALETTE["blue"], PALETTE["light_blue"], PALETTE["orange"]]
    bars = ax.bar(components, values, color=colours, width=0.5, zorder=3, edgecolor="white")
    ax.bar_label(bars, fmt="£%.2fM", padding=5, fontsize=11, fontweight="bold")

    # Total line annotation
    total = cap.total_capex_gbp / 1e6
    ax.axhline(total, color=PALETTE["red"], ls="--", lw=1.5, zorder=4)
    ax.text(2.4, total + 0.15, f"Total: £{total:.2f}M", color=PALETTE["red"],
            ha="right", fontsize=10, fontweight="bold")

    ax.set_ylabel("Capital Cost  (£M)")
    ax.set_title("Infrastructure CAPEX Breakdown")
    ax.set_ylim(0, total * 1.25)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    _savefig(fig, "capex_breakdown.png")


# ── Figure 9: Tornado Chart (LCOH sensitivity) ────────────────────────────────

def plot_tornado_lcoh():
    """
    One-at-a-time sensitivity: each parameter varied ±20% from baseline.
    Uses explicit override kwargs in calculate_lcoh — avoids the Python
    'from ... import' local-binding issue that makes monkey-patching ineffective.
    """
    baseline_lcoh = calculate_lcoh().total_dispensed_cost_gbp_kg

    # Each entry: (display label, kwarg name in calculate_lcoh, baseline value)
    params = [
        ("Electricity price",       "electricity_price_gbp_mwh",        ELECTRICITY_PRICE_GBP_MWH),
        ("Electrolyser efficiency", "electrolyser_efficiency_kwh_kg",    ELECTROLYSER_EFFICIENCY_KWH_KG),
        ("Electrolyser CAPEX",      "electrolyser_cost_per_kw",          ELECTROLYSER_COST_PER_KW),
        ("BoP fraction",            "bop_fraction",                      BOP_FRACTION),
        ("Transport cost",          "transport_cost_gbp_kg",             TRANSPORT_COST_GBP_KG),
        ("HRS OPEX",                "hrs_opex_gbp_kg_override",          HRS_OPEX_GBP_KG),
        ("Discount rate",           "discount_rate",                     DISCOUNT_RATE),
    ]

    results = []
    for label, kwarg, base_val in params:
        low_val  = calculate_lcoh(**{kwarg: base_val * 0.80}).total_dispensed_cost_gbp_kg
        high_val = calculate_lcoh(**{kwarg: base_val * 1.20}).total_dispensed_cost_gbp_kg
        results.append((label, low_val - baseline_lcoh, high_val - baseline_lcoh))

    # Sort by total swing (largest impact at top)
    results.sort(key=lambda x: abs(x[2] - x[1]), reverse=True)

    labels = [r[0] for r in results]
    lows   = [r[1] for r in results]
    highs  = [r[2] for r in results]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    y = np.arange(len(labels))

    for i, (lo, hi) in enumerate(zip(lows, highs)):
        # Bar spanning from low to high, centred on zero
        left  = min(lo, hi)
        width = abs(hi - lo)
        colour = PALETTE["red"] if hi > 0 else PALETTE["green"]
        ax.barh(i, width, left=left, height=0.5, color=colour, alpha=0.82)

        # Annotate low/high values
        ax.text(lo - 0.003, i, f"{lo:+.3f}", va="center", ha="right", fontsize=8.5)
        ax.text(hi + 0.003, i, f"{hi:+.3f}", va="center", ha="left",  fontsize=8.5)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11)
    ax.axvline(0, color="black", lw=1.3)
    ax.set_xlabel("Change in Dispensed LCOH  (£/kg H₂)")
    ax.set_title(
        f"Tornado Chart: LCOH Sensitivity to ±20% Parameter Variation\n"
        f"(Baseline LCOH = £{baseline_lcoh:.2f}/kg)"
    )

    # Custom legend
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color=PALETTE["red"],   alpha=0.82, label="Increases LCOH (+20%)"),
        Patch(color=PALETTE["green"], alpha=0.82, label="Decreases LCOH (+20%)"),
    ], fontsize=9, loc="lower right")

    fig.tight_layout()
    _savefig(fig, "lcoh_sensitivity_tornado.png")


# ── Runner ─────────────────────────────────────────────────────────────────────

def generate_all_figures():
    _set_style()
    print("Generating figures...")
    plot_lcoh_vs_electricity()
    plot_annual_cost_vs_electricity()
    plot_breakeven_diesel()
    plot_npv_vs_electricity()
    plot_irr_vs_electricity()
    plot_npv_heatmap()
    plot_emissions_comparison()
    plot_capex_breakdown()
    plot_tornado_lcoh()
    print(f"\nAll figures saved to ./{OUTPUT_DIR}/")
