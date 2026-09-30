"""Create a static dashboard preview and a data-driven executive insight report."""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
IMAGES = ROOT / "images" / "dashboard_screenshots"
DOCS = ROOT / "docs"
BRAND = "#00A19A"
DARK = "#192A3A"
ACCENT = "#F0A500"


def percent(value: float) -> str:
    return f"{value:.1%}"


def run() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    events = pd.read_csv(DATA / "FactFunnelEvents.csv", parse_dates=["stage_date"])
    purchases = pd.read_csv(DATA / "FactPurchases.csv", parse_dates=["purchase_date"])
    care = pd.read_csv(DATA / "FactCustomerCare.csv")

    acquisition = events[events["stage"] != "Repeat Purchase"]
    stages = acquisition.groupby(["stage_order", "stage"], as_index=False)["customer_id"].nunique().sort_values("stage_order")
    stages.columns = ["stage_order", "stage", "customers"]
    prospects = stages.iloc[0].customers
    initial = purchases.loc[purchases.purchase_type == "Initial", "customer_id"].nunique()
    repeat = purchases.loc[purchases.purchase_type == "Repeat", "customer_id"].nunique()
    revenue = purchases.purchase_value.sum()
    satisfaction = care.satisfaction_score.mean()
    resolution = (care.resolution_status == "Resolved").mean()

    monthly = acquisition[acquisition.stage == "Initial Interaction"].copy()
    monthly["month"] = monthly.stage_date.dt.to_period("M").astype(str)
    monthly = monthly.groupby("month").customer_id.nunique()
    channel = acquisition.groupby(["marketing_channel", "stage"], as_index=False).customer_id.nunique()
    channel = channel.pivot(index="marketing_channel", columns="stage", values="customer_id").fillna(0)
    channel["conversion"] = channel.get("Purchase", 0) / channel["Initial Interaction"]
    channel = channel.sort_values("conversion", ascending=False)
    products = purchases.groupby("product", as_index=False).agg(revenue=("purchase_value", "sum"), purchases=("purchase_id", "count")).sort_values("revenue", ascending=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(16, 10), facecolor="#F7F9FB")
    grid = fig.add_gridspec(3, 4, height_ratios=[.65, 2, 2], hspace=.52, wspace=.38)
    fig.suptitle("Funnel Intelligence | Executive Overview", x=.055, y=.975, ha="left", fontsize=22, fontweight="bold", color=DARK)
    fig.text(.055, .945, "Synthetic demo data · Jan 2024–May 2027", color="#637381", fontsize=10)
    cards = [("Prospects", f"{prospects:,}"), ("Initial Purchasers", f"{initial:,}"), ("Conversion", percent(initial / prospects)), ("Repeat Purchase", percent(repeat / initial))]
    for idx, (label, value) in enumerate(cards):
        ax = fig.add_subplot(grid[0, idx]); ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="white", zorder=0))
        ax.text(.08, .66, label, transform=ax.transAxes, fontsize=10, color="#637381")
        ax.text(.08, .24, value, transform=ax.transAxes, fontsize=22, fontweight="bold", color=DARK)

    ax_funnel = fig.add_subplot(grid[1, :2])
    ax_funnel.barh(stages.stage, stages.customers, color=[BRAND] * (len(stages) - 1) + [ACCENT])
    ax_funnel.invert_yaxis(); ax_funnel.set_title("Acquisition funnel", loc="left", fontweight="bold", color=DARK)
    ax_funnel.set_xlabel("Distinct customers"); ax_funnel.spines[["top", "right", "left"]].set_visible(False)
    for y, value in enumerate(stages.customers): ax_funnel.text(value + 55, y, f"{value:,}", va="center", fontsize=9)

    ax_channel = fig.add_subplot(grid[1, 2:])
    ax_channel.barh(channel.index, channel.conversion * 100, color=BRAND)
    ax_channel.invert_yaxis(); ax_channel.set_title("Purchase conversion by marketing channel", loc="left", fontweight="bold", color=DARK)
    ax_channel.set_xlabel("Conversion rate (%)"); ax_channel.spines[["top", "right", "left"]].set_visible(False)
    for y, value in enumerate(channel.conversion * 100): ax_channel.text(value + .08, y, f"{value:.1f}%", va="center", fontsize=9)

    ax_trend = fig.add_subplot(grid[2, :2])
    ax_trend.plot(monthly.index, monthly.values, color=BRAND, linewidth=2.5)
    ax_trend.set_title("Monthly prospect volume", loc="left", fontweight="bold", color=DARK)
    ax_trend.set_ylabel("Distinct prospects"); ax_trend.tick_params(axis="x", rotation=45); ax_trend.spines[["top", "right"]].set_visible(False)

    ax_product = fig.add_subplot(grid[2, 2:])
    ax_product.bar(products["product"], products.revenue / 1_000_000, color=[DARK, BRAND, BRAND, BRAND])
    ax_product.set_title("Purchase revenue by product", loc="left", fontweight="bold", color=DARK)
    ax_product.set_ylabel("Revenue (€M)"); ax_product.spines[["top", "right"]].set_visible(False)
    for x, value in enumerate(products.revenue / 1_000_000): ax_product.text(x, value + .03, f"€{value:.1f}M", ha="center", fontsize=9)
    fig.text(.055, .015, f"Revenue €{revenue / 1_000_000:.1f}M  |  Satisfaction {satisfaction:.1f}/5  |  Resolution rate {percent(resolution)}", color="#637381", fontsize=10)
    fig.savefig(IMAGES / "executive_overview_preview.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    best_channel = channel.index[0]
    weakest_transition = stages.assign(conversion=stages.customers / stages.customers.shift()).iloc[1:].sort_values("conversion").iloc[0]
    top_product = products.iloc[0]
    report = f"""# Executive Insight Report

Generated from the current synthetic dataset. These observations demonstrate how the dashboard should be used; they are not real Mercedes-Benz business results.

## Snapshot

- **{prospects:,}** prospects entered the acquisition funnel.
- **{initial:,}** became initial purchasers, an overall conversion rate of **{percent(initial / prospects)}**.
- Total transaction revenue is **€{revenue / 1_000_000:.2f}M**.
- **{repeat:,}** customers made a repeat purchase, a rate of **{percent(repeat / initial)}** among initial purchasers.
- Customer-care resolution rate is **{percent(resolution)}**, with an average satisfaction score of **{satisfaction:.1f}/5**.

## Priority observations

1. **{weakest_transition.stage} is the largest acquisition bottleneck.** Only **{percent(weakest_transition.conversion)}** of customers from the previous stage reach it. Sales should investigate segmentation, offer competitiveness, follow-up timing, and stock availability at this point.
2. **{best_channel} has the strongest purchase conversion** at **{percent(channel.iloc[0].conversion)}**. Marketing should assess whether its audience and campaign approach can be scaled while maintaining lead quality.
3. **{top_product['product']} leads revenue** with **€{top_product.revenue / 1_000_000:.2f}M**. Use the Sales page to determine whether this is driven by purchase volume, price, region, or a particular customer segment.

## Recommended stakeholder actions

- Marketing: compare channel volume with qualified-lead and purchase conversion—not lead volume alone.
- Sales: drill into the weakest stage by product, region, and customer segment before deciding on corrective action.
- Customer Care: compare satisfaction and repeat-purchase behavior for resolved versus unresolved cases.
- Management: review conversion, revenue, satisfaction, and retention together before prioritising investment.
"""
    (DOCS / "executive_insight_report.md").write_text(report)
    print(f"Created {IMAGES / 'executive_overview_preview.png'} and executive insight report")


if __name__ == "__main__":
    run()
