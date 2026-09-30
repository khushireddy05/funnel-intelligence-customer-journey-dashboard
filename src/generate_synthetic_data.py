"""Generate deterministic, realistic synthetic funnel data for the dashboard."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


SEED = 42
STAGES = ["Initial Interaction", "Engaged Prospect", "Lead", "Qualified Lead", "Opportunity", "Offer", "Purchase"]
CHANNELS = ["Website", "Paid Search", "Social Media", "Email", "Dealer Event", "Referral"]
PRODUCTS = ["Sprinter", "Vito", "V-Class", "VLE"]
REGIONS = {
    "Germany": "DACH", "Austria": "DACH", "France": "Western Europe",
    "Spain": "Southern Europe", "Italy": "Southern Europe", "Netherlands": "Benelux",
}


def _date_range(rng: np.random.Generator, count: int) -> pd.Series:
    start = pd.Timestamp("2024-01-01")
    return pd.Series(start + pd.to_timedelta(rng.integers(0, 700, count), unit="D"))


def generate(output_dir: Path, customer_count: int = 5_000) -> None:
    """Create source-system CSV files in *output_dir*."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    customer_ids = [f"C{n:06d}" for n in range(1, customer_count + 1)]
    countries = rng.choice(list(REGIONS), customer_count, p=[.42, .08, .18, .12, .12, .08])
    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_segment": rng.choice(["Small Business", "Fleet", "Private", "Enterprise"], customer_count, p=[.32, .23, .30, .15]),
        "customer_type": rng.choice(["New", "Existing"], customer_count, p=[.72, .28]),
        "country": countries,
        "region": [REGIONS[c] for c in countries],
        "first_seen_date": _date_range(rng, customer_count).dt.date,
    })
    customers.to_csv(output_dir / "customers.csv", index=False)

    first_dates = pd.to_datetime(customers["first_seen_date"])
    channels = rng.choice(CHANNELS, customer_count, p=[.28, .21, .16, .12, .13, .10])
    products = rng.choice(PRODUCTS, customer_count, p=[.34, .29, .20, .17])
    campaigns = {"Website": "Always-on Web", "Paid Search": "Commercial Intent", "Social Media": "Urban Mobility", "Email": "CRM Nurture", "Dealer Event": "Van Experience Days", "Referral": "Customer Referral"}

    interactions = []
    funnel_events = []
    lead_rows, opportunity_rows, purchase_rows, case_rows = [], [], [], []
    lead_counter = opportunity_counter = purchase_counter = case_counter = 0

    # Conversion probability deliberately varies by channel to create analyzable patterns.
    lead_probability = {"Website": .38, "Paid Search": .45, "Social Media": .25, "Email": .41, "Dealer Event": .52, "Referral": .57}
    qualification_probability = {"Website": .57, "Paid Search": .61, "Social Media": .43, "Email": .63, "Dealer Event": .71, "Referral": .75}

    for idx, customer_id in enumerate(customer_ids):
        first_date = first_dates.iloc[idx]
        channel, product = channels[idx], products[idx]
        interaction_id = f"I{idx + 1:07d}"
        interactions.append({"interaction_id": interaction_id, "customer_id": customer_id, "interaction_date": first_date.date(), "interaction_channel": channel, "interaction_type": "Initial Visit", "campaign": campaigns[channel], "funnel_stage": "Initial Interaction"})
        funnel_events.append({"customer_id": customer_id, "stage": "Initial Interaction", "stage_date": first_date.date(), "marketing_channel": channel, "product": product})

        engaged = rng.random() < .72
        if not engaged:
            continue
        engaged_date = first_date + pd.Timedelta(days=int(rng.integers(1, 15)))
        interactions.append({"interaction_id": f"I{len(interactions)+1:07d}", "customer_id": customer_id, "interaction_date": engaged_date.date(), "interaction_channel": channel, "interaction_type": rng.choice(["Brochure Download", "Configurator", "Event Registration", "Callback Request"]), "campaign": campaigns[channel], "funnel_stage": "Engaged Prospect"})
        funnel_events.append({"customer_id": customer_id, "stage": "Engaged Prospect", "stage_date": engaged_date.date(), "marketing_channel": channel, "product": product})

        if rng.random() >= lead_probability[channel]:
            continue
        lead_counter += 1
        lead_date = engaged_date + pd.Timedelta(days=int(rng.integers(1, 22)))
        lead_id = f"L{lead_counter:06d}"
        lead_rows.append({"lead_id": lead_id, "customer_id": customer_id, "lead_date": lead_date.date(), "lead_source": channel, "campaign": campaigns[channel], "lead_status": "Created", "product": product})
        funnel_events.append({"customer_id": customer_id, "stage": "Lead", "stage_date": lead_date.date(), "marketing_channel": channel, "product": product})

        if rng.random() >= qualification_probability[channel]:
            continue
        qualified_date = lead_date + pd.Timedelta(days=int(rng.integers(1, 16)))
        lead_rows[-1]["qualified_date"] = qualified_date.date()
        lead_rows[-1]["lead_status"] = "Qualified"
        funnel_events.append({"customer_id": customer_id, "stage": "Qualified Lead", "stage_date": qualified_date.date(), "marketing_channel": channel, "product": product})

        if rng.random() >= .74:
            continue
        opportunity_counter += 1
        opportunity_date = qualified_date + pd.Timedelta(days=int(rng.integers(2, 22)))
        offer_date = opportunity_date + pd.Timedelta(days=int(rng.integers(2, 25)))
        opportunity_id = f"O{opportunity_counter:06d}"
        opportunity_rows.append({"opportunity_id": opportunity_id, "lead_id": lead_id, "customer_id": customer_id, "opportunity_date": opportunity_date.date(), "offer_date": offer_date.date(), "product": product, "sales_channel": rng.choice(["Dealer", "Direct Sales", "Online"], p=[.64, .26, .10]), "opportunity_status": "Offer Created"})
        funnel_events.extend([
            {"customer_id": customer_id, "stage": "Opportunity", "stage_date": opportunity_date.date(), "marketing_channel": channel, "product": product},
            {"customer_id": customer_id, "stage": "Offer", "stage_date": offer_date.date(), "marketing_channel": channel, "product": product},
        ])

        # About half of offers convert; referral and dealer event leads perform better.
        purchase_probability = .57 if channel in {"Referral", "Dealer Event"} else .46
        if rng.random() >= purchase_probability:
            continue
        purchase_counter += 1
        purchase_date = offer_date + pd.Timedelta(days=int(rng.integers(4, 50)))
        value = {"Sprinter": 54000, "Vito": 43000, "V-Class": 69000, "VLE": 61000}[product] + int(rng.normal(0, 4500))
        purchase_rows.append({"purchase_id": f"P{purchase_counter:06d}", "customer_id": customer_id, "purchase_date": purchase_date.date(), "product": product, "purchase_value": max(value, 20000), "purchase_type": "Initial", "marketing_channel": channel})
        funnel_events.append({"customer_id": customer_id, "stage": "Purchase", "stage_date": purchase_date.date(), "marketing_channel": channel, "product": product})

        # 45% of purchasers contact care, and 20% make a second purchase.
        if rng.random() < .45:
            case_counter += 1
            opened = purchase_date + pd.Timedelta(days=int(rng.integers(5, 190)))
            resolution_hours = int(rng.gamma(2.5, 18))
            resolved = rng.random() < .89
            satisfaction = int(np.clip(round(5.5 - resolution_hours / 55 + rng.normal(0, .8)), 1, 5)) if resolved else int(rng.integers(1, 4))
            case_rows.append({"case_id": f"CS{case_counter:06d}", "customer_id": customer_id, "opened_date": opened.date(), "contact_channel": rng.choice(["Phone", "Email", "Dealer", "Chat"]), "case_category": rng.choice(["Maintenance", "Vehicle Issue", "Finance", "Delivery", "Digital Services"]), "resolution_status": "Resolved" if resolved else "Open", "resolution_hours": resolution_hours if resolved else np.nan, "satisfaction_score": satisfaction})

        if rng.random() < .20:
            purchase_counter += 1
            repeat_date = purchase_date + pd.Timedelta(days=int(rng.integers(120, 520)))
            repeat_product = rng.choice(PRODUCTS, p=[.33, .28, .22, .17])
            value = {"Sprinter": 54000, "Vito": 43000, "V-Class": 69000, "VLE": 61000}[repeat_product] + int(rng.normal(0, 4500))
            purchase_rows.append({"purchase_id": f"P{purchase_counter:06d}", "customer_id": customer_id, "purchase_date": repeat_date.date(), "product": repeat_product, "purchase_value": max(value, 20000), "purchase_type": "Repeat", "marketing_channel": channel})
            funnel_events.append({"customer_id": customer_id, "stage": "Repeat Purchase", "stage_date": repeat_date.date(), "marketing_channel": channel, "product": repeat_product})

    pd.DataFrame(interactions).to_csv(output_dir / "interactions.csv", index=False)
    pd.DataFrame(funnel_events).to_csv(output_dir / "funnel_events.csv", index=False)
    pd.DataFrame(lead_rows).to_csv(output_dir / "leads.csv", index=False)
    pd.DataFrame(opportunity_rows).to_csv(output_dir / "opportunities.csv", index=False)
    pd.DataFrame(purchase_rows).to_csv(output_dir / "purchases.csv", index=False)
    pd.DataFrame(case_rows).to_csv(output_dir / "customer_care.csv", index=False)


if __name__ == "__main__":
    generate(Path("data/raw"))
