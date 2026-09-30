"""Validate raw source data and publish Power BI-ready analytical tables."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.generate_synthetic_data import STAGES, generate


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
QUALITY_DIR = ROOT / "data" / "quality"
DATE_COLUMNS = {
    "customers": ["first_seen_date"], "interactions": ["interaction_date"],
    "funnel_events": ["stage_date"], "leads": ["lead_date", "qualified_date"],
    "opportunities": ["opportunity_date", "offer_date"], "purchases": ["purchase_date"],
    "customer_care": ["opened_date"],
}


def read_sources() -> dict[str, pd.DataFrame]:
    sources = {}
    for name, columns in DATE_COLUMNS.items():
        frame = pd.read_csv(RAW_DIR / f"{name}.csv")
        for column in columns:
            if column in frame:
                frame[column] = pd.to_datetime(frame[column], errors="coerce")
        sources[name] = frame
    return sources


def validate(sources: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Return documented quality checks; pipeline halts only on critical failures."""
    checks = []
    customer_ids = set(sources["customers"]["customer_id"])
    for name, frame in sources.items():
        checks.append({"dataset": name, "check": "Duplicate rows", "issue_count": int(frame.duplicated().sum()), "severity": "Warning"})
        checks.append({"dataset": name, "check": "Missing required customer ID", "issue_count": int(frame["customer_id"].isna().sum()) if "customer_id" in frame else 0, "severity": "Critical"})
        # Qualified date is intentionally blank until a lead becomes qualified.
        required_dates = [column for column in DATE_COLUMNS[name] if not (name == "leads" and column == "qualified_date")]
        for column in required_dates:
            checks.append({"dataset": name, "check": f"Invalid or missing {column}", "issue_count": int(frame[column].isna().sum()), "severity": "Warning"})
        if name != "customers" and "customer_id" in frame:
            checks.append({"dataset": name, "check": "Unknown customer ID", "issue_count": int((~frame["customer_id"].isin(customer_ids)).sum()), "severity": "Critical"})
    events = sources["funnel_events"]
    checks.append({"dataset": "funnel_events", "check": "Unknown funnel stage", "issue_count": int((~events["stage"].isin(STAGES + ["Repeat Purchase"])).sum()), "severity": "Critical"})
    purchases = sources["purchases"]
    checks.append({"dataset": "purchases", "check": "Non-positive purchase value", "issue_count": int((purchases["purchase_value"] <= 0).sum()), "severity": "Critical"})
    return pd.DataFrame(checks)


def build_model(sources: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    customers = sources["customers"].copy()
    products = pd.DataFrame({"product": ["Sprinter", "Vito", "V-Class", "VLE"], "product_category": ["Large Van", "Mid-size Van", "Premium MPV", "Electric Van"]})
    channels = pd.concat([
        sources["interactions"][["interaction_channel"]].rename(columns={"interaction_channel": "channel"}),
        sources["opportunities"][["sales_channel"]].rename(columns={"sales_channel": "channel"}),
        sources["customer_care"][["contact_channel"]].rename(columns={"contact_channel": "channel"}),
    ]).drop_duplicates().sort_values("channel").reset_index(drop=True)
    stages = pd.DataFrame({"stage": STAGES + ["Repeat Purchase"], "stage_order": range(1, len(STAGES) + 2)})
    min_date = min(frame[column].min() for name, frame in sources.items() for column in DATE_COLUMNS[name] if column in frame and frame[column].notna().any())
    max_date = max(frame[column].max() for name, frame in sources.items() for column in DATE_COLUMNS[name] if column in frame and frame[column].notna().any())
    dates = pd.DataFrame({"date": pd.date_range(min_date, max_date, freq="D")})
    dates["year"] = dates["date"].dt.year
    dates["month_number"] = dates["date"].dt.month
    dates["month"] = dates["date"].dt.strftime("%b")
    dates["year_month"] = dates["date"].dt.strftime("%Y-%m")

    events = sources["funnel_events"].copy().merge(stages, on="stage", how="left")
    events = events.merge(customers[["customer_id", "region", "country", "customer_segment", "customer_type"]], on="customer_id", how="left")
    events = events.sort_values(["customer_id", "stage_order", "stage_date"]).drop_duplicates(["customer_id", "stage"], keep="first")
    events["previous_stage_date"] = events.groupby("customer_id")["stage_date"].shift()
    events["days_from_previous_stage"] = (events["stage_date"] - events["previous_stage_date"]).dt.days

    return {
        "DimCustomer": customers,
        "DimProduct": products,
        "DimChannel": channels,
        "DimFunnelStage": stages,
        "DimDate": dates,
        "FactInteractions": sources["interactions"],
        "FactLeads": sources["leads"],
        "FactOpportunities": sources["opportunities"],
        "FactPurchases": sources["purchases"],
        "FactCustomerCare": sources["customer_care"],
        "FactFunnelEvents": events,
    }


def run() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    generate(RAW_DIR)
    sources = read_sources()
    report = validate(sources)
    report.to_csv(QUALITY_DIR / "data_quality_report.csv", index=False)
    critical = report.loc[(report["severity"] == "Critical") & (report["issue_count"] > 0)]
    if not critical.empty:
        raise ValueError(f"Critical data-quality failures found:\n{critical.to_string(index=False)}")
    for name, frame in build_model(sources).items():
        frame.to_csv(PROCESSED_DIR / f"{name}.csv", index=False, date_format="%Y-%m-%d")
    print(f"Pipeline complete: {len(sources['customers']):,} customers; outputs in {PROCESSED_DIR}")


if __name__ == "__main__":
    run()
