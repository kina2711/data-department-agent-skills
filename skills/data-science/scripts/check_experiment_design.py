#!/usr/bin/env python3
"""Check an experiment design before it runs, when the sample size still matters.

Most disappointing experiments were underpowered on day one: the minimum detectable effect was
chosen after the fact, the variance was assumed, several metrics were tested without correction,
or the plan allowed peeking until the p-value cooperated. All of that is decidable before a single
user is exposed.

It computes the required sample size for the stated design and reports what the planned traffic
can actually detect. It uses a normal approximation, assumes independent units and a fixed horizon,
and cannot rescue a design whose metric or randomization unit is wrong.
"""

from __future__ import annotations

import argparse
import math
import sys

# Two-sided normal quantiles for the alpha levels an experiment plan realistically uses.
Z_ALPHA_TWO_SIDED = {0.20: 1.2816, 0.10: 1.6449, 0.05: 1.9600, 0.01: 2.5758, 0.005: 2.8070}
Z_POWER = {0.70: 0.5244, 0.80: 0.8416, 0.85: 1.0364, 0.90: 1.2816, 0.95: 1.6449}


def nearest(table: dict[float, float], value: float) -> float:
    key = min(table, key=lambda candidate: abs(candidate - value))
    return table[key]


def proportion_sample_size(baseline: float, mde_absolute: float, alpha: float, power: float) -> int:
    """Per-arm sample size for a two-sided test of two independent proportions."""
    treatment = baseline + mde_absolute
    treatment = min(max(treatment, 1e-6), 1 - 1e-6)
    pooled = (baseline + treatment) / 2
    z_alpha = nearest(Z_ALPHA_TWO_SIDED, alpha)
    z_beta = nearest(Z_POWER, power)
    numerator = (
        z_alpha * math.sqrt(2 * pooled * (1 - pooled))
        + z_beta * math.sqrt(baseline * (1 - baseline) + treatment * (1 - treatment))
    ) ** 2
    return math.ceil(numerator / (mde_absolute ** 2))


def mean_sample_size(std: float, mde_absolute: float, alpha: float, power: float) -> int:
    """Per-arm sample size for a two-sided test of two independent means."""
    z_alpha = nearest(Z_ALPHA_TWO_SIDED, alpha)
    z_beta = nearest(Z_POWER, power)
    return math.ceil(2 * ((std * (z_alpha + z_beta)) / mde_absolute) ** 2)


def detectable_effect(available_per_arm: int, baseline: float, alpha: float, power: float) -> float:
    """Smallest absolute effect the available traffic can detect, found by bisection."""
    low, high = 1e-6, min(baseline, 1 - baseline)
    if high <= low:
        return float("nan")
    for _ in range(80):
        mid = (low + high) / 2
        if proportion_sample_size(baseline, mid, alpha, power) > available_per_arm:
            low = mid
        else:
            high = mid
    return high


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--metric", choices=("proportion", "mean"), default="proportion")
    parser.add_argument("--baseline", type=float, help="baseline conversion rate, 0-1 (proportion metrics)")
    parser.add_argument("--std", type=float, help="baseline standard deviation (mean metrics)")
    parser.add_argument("--mde", type=float, required=True, help="minimum detectable effect; absolute unless --relative")
    parser.add_argument("--relative", action="store_true", help="treat --mde as a relative lift of the baseline")
    parser.add_argument("--alpha", type=float, default=0.05, help="two-sided significance level (default 0.05)")
    parser.add_argument("--power", type=float, default=0.80, help="target power (default 0.80)")
    parser.add_argument("--arms", type=int, default=2, help="number of arms including control (default 2)")
    parser.add_argument("--daily-units", type=float, help="units entering the experiment per day, across all arms")
    parser.add_argument("--max-days", type=float, help="the longest the experiment may run")
    parser.add_argument("--metrics-tested", type=int, default=1, help="how many metrics are tested for significance")
    parser.add_argument("--correction", choices=("none", "bonferroni"), default="none")
    args = parser.parse_args()

    warnings: list[str] = []
    errors: list[str] = []

    if args.metric == "proportion":
        if args.baseline is None:
            errors.append("--baseline is required for a proportion metric")
        elif not 0 < args.baseline < 1:
            errors.append("--baseline must be strictly between 0 and 1")
    elif args.std is None or args.std <= 0:
        errors.append("--std must be a positive number for a mean metric")

    if args.mde <= 0:
        errors.append("--mde must be positive")
    if args.arms < 2:
        errors.append("--arms must be at least 2")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(2)

    alpha = args.alpha
    if args.correction == "bonferroni" and args.metrics_tested > 1:
        alpha = args.alpha / args.metrics_tested
        print(f"alpha corrected for {args.metrics_tested} metrics: {args.alpha} -> {alpha:.5f} (Bonferroni)")
    elif args.metrics_tested > 1:
        warnings.append(
            f"{args.metrics_tested} metrics tested at alpha {args.alpha} with no correction; "
            f"the chance of at least one false positive is about {1 - (1 - args.alpha) ** args.metrics_tested:.0%}"
        )

    if args.metric == "proportion":
        mde_absolute = args.baseline * args.mde if args.relative else args.mde
        if args.baseline + mde_absolute >= 1:
            print("ERROR: baseline plus effect reaches or exceeds 1; restate the effect")
            sys.exit(2)
        per_arm = proportion_sample_size(args.baseline, mde_absolute, alpha, args.power)
        print(f"metric: proportion  baseline: {args.baseline:.4f}  absolute MDE: {mde_absolute:.4f}")
    else:
        mde_absolute = args.mde
        per_arm = mean_sample_size(args.std, mde_absolute, alpha, args.power)
        print(f"metric: mean  std: {args.std}  absolute MDE: {mde_absolute}")

    total = per_arm * args.arms
    print(f"alpha: {alpha:.5f} (two-sided)  power: {args.power}  arms: {args.arms}")
    print(f"required per arm: {per_arm:,}  total: {total:,}")

    if args.daily_units:
        days = total / args.daily_units
        print(f"at {args.daily_units:,.0f} units/day: {days:.1f} days to reach the required sample")
        if days < 7:
            warnings.append(
                f"the design completes in {days:.1f} days; run at least one full week anyway so weekday "
                "and weekend behaviour are both represented"
            )
        if args.max_days and days > args.max_days:
            available_per_arm = int(args.daily_units * args.max_days / args.arms)
            print(f"available per arm within {args.max_days:.0f} days: {available_per_arm:,}")
            if args.metric == "proportion":
                floor = detectable_effect(available_per_arm, args.baseline, alpha, args.power)
                relative = floor / args.baseline
                print(
                    f"FAILED: underpowered. Within the horizon the design can only detect about "
                    f"{floor:.4f} absolute ({relative:.1%} relative), not {mde_absolute:.4f}."
                )
            else:
                print(f"FAILED: underpowered. {total:,} units are needed but only {available_per_arm * args.arms:,} are available.")
            print("Raise the MDE, extend the horizon, reduce arms, or pick a lower-variance metric. Do not run and hope.")
            sys.exit(1)

    for warning in warnings:
        print(f"WARNING: {warning}")
    print("NOTE: fixed-horizon design. Stopping early on a significant result inflates the false-positive rate; use a sequential method if you need to peek.")

    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to resolve before launch")
        sys.exit(0)
    print("PASS: the design reaches the stated power within the stated constraints")


if __name__ == "__main__":
    main()
