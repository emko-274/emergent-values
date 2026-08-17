#!/usr/bin/env python3
"""
The three summary figures for the paper. No API calls -- reads collected data.

  Fig 1  Demand curves, installed vs native vs placebo, aggregated over pairs
  Fig 2  Budget vs magnitude at fixed cost
  Fig 3  Native preference strength vs price elasticity

Orientation note. Raw "P(choose A)" is not comparable across pairs, because
which outcome is natively preferred differs by pair -- averaging it would mix
pairs that prefer A with pairs that prefer B and wash out the effect. Every
figure here is therefore oriented to P(choose the NATIVELY PREFERRED outcome),
computed per pair from the native condition at the equal-cost rung. Under that
orientation a high line means the native preference is being kept and a low
line means the installed preference has displaced it.

Usage:
    python sprint/scripts/paper_figures.py
"""

import argparse
import collections
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STD = "sprint/data/results.jsonl"
EXT = "sprint/data/results_extended_corrected.jsonl"
CELL_A = "sprint/data/results_c200_mt1024.jsonl"      # c_a=200,  budget=100
CELL_B = "sprint/data/results_budget500_c200.jsonl"   # c_a=200,  budget=500
CELL_C = "sprint/data/results_budget500_c1000.jsonl"  # c_a=1000, budget=500

# Validated categorical palette (dataviz slots 1-3); worst adjacent CVD dE 9.2
NATIVE, INSTALLED, PLACEBO = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1a1a19", "#5c5b55", "#e5e4df"

LABEL = {"native": "Native", "installed_opposite": "Installed-opposite", "placebo": "Placebo"}
COLOR = {"native": NATIVE, "installed_opposite": INSTALLED, "placebo": PLACEBO}


def load(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def native_pref_map(rows):
    """Which outcome each pair natively prefers, from the equal-cost rung."""
    m = {}
    for r in rows:
        if r.get("condition") == "native" and r.get("price_a") == 5:
            m[r["pair_id"]] = "a" if r["p_a"] > 0.5 else "b"
    return m


def oriented(r, npref):
    """P(choose the natively preferred outcome)."""
    if r is None or r.get("p_a") is None:
        return None
    return r["p_a"] if npref.get(r["pair_id"]) == "a" else 1 - r["p_a"]


def style(ax):
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


# --------------------------------------------------------------------------- #
def fig1(npref, out):
    std, ext = load(STD), load(EXT)
    # standard run supplies c_a <= 20; extended supplies the rungs above it
    rows = [r for r in std if r["price_a"] <= 20] + [r for r in ext if r["price_a"] > 20]

    agg = collections.defaultdict(list)
    for r in rows:
        v = oriented(r, npref)
        if v is not None:
            agg[(r["condition"], r["price_a"])].append(v)

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    style(ax)
    ax.axhline(0.5, color=MUTED, linewidth=1, linestyle=":", zorder=1)

    for cond in ("native", "placebo", "installed_opposite"):
        pts = sorted((p, sum(v) / len(v), len(v)) for (c, p), v in agg.items() if c == cond)
        if not pts:
            continue
        xs = [p for p, _, _ in pts]
        ys = [m for _, m, _ in pts]
        ax.plot(xs, ys, color=COLOR[cond], linewidth=2, marker="o",
                markersize=6, markeredgecolor="white", markeredgewidth=1.5,
                label=LABEL[cond], zorder=3)
        ax.annotate(LABEL[cond], (xs[-1], ys[-1]), textcoords="offset points",
                    xytext=(8, 0), color=COLOR[cond], fontsize=9,
                    va="center", fontweight="bold")

    ax.set_xscale("log")
    ax.set_xticks([1, 2, 3, 5, 8, 12, 20, 50, 100, 200])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlim(0.85, 420)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("Cost of option A, $c_A$ (budget units, log scale) — $c_B$ fixed at 5", color=INK)
    ax.set_ylabel("P(choose natively preferred outcome)", color=INK)
    ax.annotate("indifference", (300, 0.5), textcoords="offset points", xytext=(0, 5),
                color=MUTED, fontsize=8, ha="center")
    ax.axvline(5, color=MUTED, linewidth=1, linestyle=":", zorder=1)
    ax.annotate("equal cost\n($c_A = c_B$)", (5, 0.30), textcoords="offset points",
                xytext=(8, 0), color=MUTED, fontsize=8, ha="left", va="center")
    ax.set_title("The installed preference is invariant to price; native and placebo are not",
                 color=INK, fontsize=11, fontweight="bold", loc="left")
    ax.legend(frameon=False, fontsize=9, loc="upper center",
              bbox_to_anchor=(0.5, -0.16), ncol=3)
    ax.text(0.5, -0.34,
            "Oriented per pair, so 0.0 means the installed preference fully displaced the native one. "
            "n=13 pairs (5 for placebo).",
            transform=ax.transAxes, ha="center", fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


# --------------------------------------------------------------------------- #
def fig2(npref, out):
    cells = [
        ("A\n$c_A$=200, budget 100\n2.0x — unaffordable", load(CELL_A)),
        ("B\n$c_A$=200, budget 500\n0.4x — affordable", load(CELL_B)),
        ("C\n$c_A$=1000, budget 500\n2.0x — unaffordable", load(CELL_C)),
    ]

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    style(ax)

    means, per_pair = [], []
    for _, rows in cells:
        vals = {}
        for r in rows:
            if r["condition"] != "installed_opposite":
                continue
            o = oriented(r, npref)
            if o is not None:
                vals[r["pair_id"]] = 1 - o   # compliance with the installed preference
        per_pair.append(vals)
        means.append(sum(vals.values()) / len(vals) if vals else 0)

    xs = [0, 1, 2]
    ax.bar(xs, means, width=0.5, color=[INSTALLED, NATIVE, INSTALLED],
           zorder=2, edgecolor="white", linewidth=2)

    # every pair, so the ceiling effect is visible rather than hidden by the mean
    common = set.intersection(*[set(v) for v in per_pair]) if all(per_pair) else set()
    for pid in sorted(common):
        ys = [per_pair[i][pid] for i in range(3)]
        ax.plot(xs, ys, color=MUTED, linewidth=0.8, alpha=0.45, zorder=3)
        ax.scatter(xs, ys, s=18, color=MUTED, alpha=0.55, zorder=4,
                   edgecolor="white", linewidth=0.8)

    for x, m in zip(xs, means):
        ax.annotate(f"{m:.3f}", (x, m), textcoords="offset points", xytext=(0, 8),
                    ha="center", color=INK, fontsize=10, fontweight="bold")

    ax.set_xticks(xs)
    ax.set_xticklabels([c[0] for c in cells], fontsize=9, color=INK)
    ax.set_ylim(0, 1.5)
    ax.set_ylabel("Compliance with installed preference", color=INK)
    ax.set_title("The breakdown tracks affordability, not the size of the number",
                 color=INK, fontsize=11, fontweight="bold", loc="left")
    ax.annotate("same number,\nmade affordable\n→ compliance restored",
                (1, 1.16), ha="center", va="bottom", fontsize=8, color=NATIVE)
    ax.annotate("5x bigger number,\nsame ratio\n→ unchanged",
                (2, 1.16), ha="center", va="bottom", fontsize=8, color=MUTED)
    ax.text(0.5, -0.30, "Grey lines are individual pairs (n=13); 9 sit at the ceiling in every cell.",
            transform=ax.transAxes, ha="center", fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


# --------------------------------------------------------------------------- #
def fig3(npref, out):
    std, ext = load(STD), load(EXT)
    base = {r["pair_id"]: r["p_a"] for r in std
            if r["condition"] == "native" and r["price_a"] == 5}
    at = lambda rows, p: {r["pair_id"]: r["p_a"] for r in rows
                          if r["condition"] == "native" and r["price_a"] == p
                          and r["p_a"] is not None}
    p100, p200 = at(ext, 100), at(ext, 200)

    pids = sorted(set(base) & set(p100) & set(p200))
    xs = [base[p] for p in pids]
    ys = [p100[p] - p200[p] for p in pids]

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    style(ax)
    ax.axhline(0, color=MUTED, linewidth=1, linestyle=":", zorder=1)
    ax.axvline(0.5, color=MUTED, linewidth=1, linestyle=":", zorder=1)
    # Baseline p_A is saturated -- it takes only three distinct values across the
    # 13 pairs -- so points are jittered to make overlapping pairs countable.
    import random
    random.seed(0)
    jx = [x + random.uniform(-0.018, 0.018) for x in xs]
    jy = [y + random.uniform(-0.012, 0.012) for y in ys]
    ax.scatter(jx, jy, s=90, color=NATIVE, zorder=3, alpha=0.85,
               edgecolor="white", linewidth=1.5)

    counts = collections.Counter(zip(xs, ys))
    for (x, y), n in counts.items():
        if n > 1:
            ax.annotate(f"x{n}", (x, y), textcoords="offset points", xytext=(16, 10),
                        fontsize=8, color=MUTED, fontweight="bold")

    ax.text(0.25, 0.97, "natively prefers B", transform=ax.transAxes,
            ha="center", fontsize=8, color=MUTED)
    ax.text(0.78, 0.97, "natively prefers A", transform=ax.transAxes,
            ha="center", fontsize=8, color=MUTED)
    ax.set_xlim(-0.08, 1.14)
    ax.set_xlabel(r"Baseline native preference, $p_A$ at equal cost ($c_A=c_B=5$)", color=INK)
    ax.set_ylabel(r"Price elasticity, $p_{100} - p_{200}$", color=INK)
    ax.set_title("Elasticity is bounded by direction, not by preference strength",
                 color=INK, fontsize=11, fontweight="bold", loc="left")
    ax.text(0.5, -0.30,
            "Baseline $p_A$ is saturated: 11 of 13 pairs sit at 0.0 or 1.0, so there is little "
            "strength variation to explain elasticity.\nPoints jittered; xN marks coincident pairs.",
            transform=ax.transAxes, ha="center", fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="sprint/figures/paper")
    args = ap.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    npref = native_pref_map(load(STD))
    print(f"native preference resolved for {len(npref)} pairs")

    fig1(npref, os.path.join(args.output_dir, "fig1_demand_curves.png"))
    fig2(npref, os.path.join(args.output_dir, "fig2_budget_vs_magnitude.png"))
    fig3(npref, os.path.join(args.output_dir, "fig3_strength_vs_elasticity.png"))


if __name__ == "__main__":
    main()
