"""Interactive Funnel Intelligence dashboard for Streamlit Community Cloud."""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"
PRIMARY = "#00A19A"
ACCENT = "#F0A500"


st.set_page_config(page_title="Funnel Intelligence", page_icon="📈", layout="wide")


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    events = pd.read_csv(DATA / "FactFunnelEvents.csv", parse_dates=["stage_date", "previous_stage_date"])
    purchases = pd.read_csv(DATA / "FactPurchases.csv", parse_dates=["purchase_date"])
    care = pd.read_csv(DATA / "FactCustomerCare.csv", parse_dates=["opened_date"])
    interactions = pd.read_csv(DATA / "FactInteractions.csv", parse_dates=["interaction_date"])
    customers = pd.read_csv(DATA / "DimCustomer.csv", parse_dates=["first_seen_date"])
    opportunities = pd.read_csv(DATA / "FactOpportunities.csv", parse_dates=["opportunity_date", "offer_date"])
    return {"events": events, "purchases": purchases, "care": care, "interactions": interactions, "customers": customers, "opportunities": opportunities}


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def euro(value: float) -> str:
    return f"€{value / 1_000_000:.2f}M" if value >= 1_000_000 else f"€{value:,.0f}"


def apply_filters(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    events = data["events"].copy()
    with st.sidebar:
        st.header("Filters")
        min_date, max_date = events.stage_date.min().date(), events.stage_date.max().date()
        dates = st.date_input("Reporting period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if len(dates) == 2:
            start, end = pd.Timestamp(dates[0]), pd.Timestamp(dates[1])
        else:
            start = end = pd.Timestamp(dates[0])
        region = st.multiselect("Region", sorted(events.region.dropna().unique()))
        country = st.multiselect("Country", sorted(events.country.dropna().unique()))
        product = st.multiselect("Product", sorted(events["product"].dropna().unique()))
        segment = st.multiselect("Customer segment", sorted(events.customer_segment.dropna().unique()))
        channel = st.multiselect("Marketing channel", sorted(events.marketing_channel.dropna().unique()))

    mask = events.stage_date.between(start, end)
    for column, selected in [("region", region), ("country", country), ("product", product), ("customer_segment", segment), ("marketing_channel", channel)]:
        if selected:
            mask &= events[column].isin(selected)
    events = events.loc[mask].copy()
    customer_ids = set(events.customer_id)
    output = {"events": events, "customers": data["customers"][data["customers"].customer_id.isin(customer_ids)]}
    output["purchases"] = data["purchases"][(data["purchases"].customer_id.isin(customer_ids)) & data["purchases"].purchase_date.between(start, end)]
    output["care"] = data["care"][(data["care"].customer_id.isin(customer_ids)) & data["care"].opened_date.between(start, end)]
    output["interactions"] = data["interactions"][(data["interactions"].customer_id.isin(customer_ids)) & data["interactions"].interaction_date.between(start, end)]
    output["opportunities"] = data["opportunities"][(data["opportunities"].customer_id.isin(customer_ids)) & data["opportunities"].opportunity_date.between(start, end)]
    return output


def kpi_cards(data: dict[str, pd.DataFrame]) -> None:
    events, purchases, care = data["events"], data["purchases"], data["care"]
    prospects = events.loc[events.stage == "Initial Interaction", "customer_id"].nunique()
    initial = purchases.loc[purchases.purchase_type == "Initial", "customer_id"].nunique()
    repeat = purchases.loc[purchases.purchase_type == "Repeat", "customer_id"].nunique()
    resolution = safe_divide((care.resolution_status == "Resolved").sum(), len(care))
    values = [("Prospects", f"{prospects:,}"), ("Initial purchasers", f"{initial:,}"), ("Conversion", f"{safe_divide(initial, prospects):.1%}"), ("Revenue", euro(purchases.purchase_value.sum())), ("Repeat purchase", f"{safe_divide(repeat, initial):.1%}"), ("Resolution rate", f"{resolution:.1%}")]
    for column, (label, value) in zip(st.columns(6), values):
        column.metric(label, value)


def executive_page(data: dict[str, pd.DataFrame]) -> None:
    st.subheader("Executive Overview")
    kpi_cards(data)
    events, purchases = data["events"], data["purchases"]
    acquisition = events[events.stage != "Repeat Purchase"]
    funnel = acquisition.groupby(["stage_order", "stage"], as_index=False).customer_id.nunique().sort_values("stage_order")
    monthly = acquisition[acquisition.stage == "Initial Interaction"].assign(month=lambda x: x.stage_date.dt.to_period("M").astype(str)).groupby("month", as_index=False).customer_id.nunique()
    channel = acquisition.groupby(["marketing_channel", "stage"], as_index=False).customer_id.nunique().pivot(index="marketing_channel", columns="stage", values="customer_id").fillna(0)
    channel["conversion"] = channel.get("Purchase", 0) / channel["Initial Interaction"]
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.funnel(funnel, y="stage", x="customer_id", color_discrete_sequence=[PRIMARY], title="Acquisition funnel"), width="stretch")
    with right:
        st.plotly_chart(px.bar(channel.reset_index().sort_values("conversion"), x="conversion", y="marketing_channel", orientation="h", text_auto=".1%", color_discrete_sequence=[PRIMARY], title="Purchase conversion by channel").update_layout(xaxis_tickformat=".0%"), width="stretch")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.line(monthly, x="month", y="customer_id", markers=True, color_discrete_sequence=[PRIMARY], title="Monthly prospect volume"), width="stretch")
    with right:
        revenue = purchases.groupby("product", as_index=False).purchase_value.sum().sort_values("purchase_value", ascending=False)
        st.plotly_chart(px.bar(revenue, x="product", y="purchase_value", text_auto=".2s", color="product", title="Revenue by product").update_layout(showlegend=False, yaxis_tickprefix="€"), width="stretch")


def funnel_page(data: dict[str, pd.DataFrame]) -> None:
    st.subheader("Funnel Analysis")
    events = data["events"]
    acquisition = events[events.stage != "Repeat Purchase"]
    stages = acquisition.groupby(["stage_order", "stage"], as_index=False).customer_id.nunique().sort_values("stage_order")
    stages["stage_conversion"] = stages.customer_id / stages.customer_id.shift()
    stages["drop_off"] = 1 - stages.stage_conversion
    stages["average_days_from_previous"] = acquisition.groupby("stage", as_index=False).days_from_previous_stage.mean().set_index("stage").reindex(stages.stage).days_from_previous_stage.values
    st.plotly_chart(px.funnel(stages, y="stage", x="customer_id", text="customer_id", color_discrete_sequence=[PRIMARY], title="Customer progression through acquisition stages"), width="stretch")
    display = stages[["stage", "customer_id", "stage_conversion", "drop_off", "average_days_from_previous"]].copy()
    display.columns = ["Stage", "Customers", "Stage conversion", "Drop-off", "Avg. days from previous stage"]
    st.dataframe(display.style.format({"Stage conversion": "{:.1%}", "Drop-off": "{:.1%}", "Avg. days from previous stage": "{:.1f}"}), width="stretch", hide_index=True)
    breakdown = acquisition[acquisition.stage == "Purchase"].groupby(["region", "product"], as_index=False).customer_id.nunique()
    st.plotly_chart(px.sunburst(breakdown, path=["region", "product"], values="customer_id", color="customer_id", color_continuous_scale="Teal", title="Purchasers by region and product"), width="stretch")


def marketing_page(data: dict[str, pd.DataFrame]) -> None:
    st.subheader("Marketing Analysis")
    events = data["events"]
    by_channel = events[events.stage.isin(["Initial Interaction", "Lead", "Qualified Lead", "Purchase"])].groupby(["marketing_channel", "stage"], as_index=False).customer_id.nunique()
    st.plotly_chart(px.bar(by_channel, x="marketing_channel", y="customer_id", color="stage", barmode="group", title="Customer journey volume by marketing channel", color_discrete_sequence=px.colors.qualitative.Safe), width="stretch")
    interactions = data["interactions"].groupby(["campaign", "interaction_type"], as_index=False).interaction_id.count()
    st.plotly_chart(px.bar(interactions, x="campaign", y="interaction_id", color="interaction_type", title="Campaign engagement by interaction type"), width="stretch")


def sales_page(data: dict[str, pd.DataFrame]) -> None:
    st.subheader("Sales Analysis")
    purchases, opportunities = data["purchases"], data["opportunities"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Opportunities", f"{opportunities.opportunity_id.nunique():,}")
    c2.metric("Offers", f"{opportunities.offer_date.notna().sum():,}")
    c3.metric("Revenue", euro(purchases.purchase_value.sum()))
    left, right = st.columns(2)
    with left:
        sales = purchases.groupby("product", as_index=False).agg(revenue=("purchase_value", "sum"), transactions=("purchase_id", "count"))
        st.plotly_chart(px.bar(sales, x="product", y="revenue", text="transactions", color="product", title="Revenue and transactions by product").update_layout(showlegend=False, yaxis_tickprefix="€"), width="stretch")
    with right:
        cycle = opportunities.assign(days_to_offer=(opportunities.offer_date - opportunities.opportunity_date).dt.days)
        st.plotly_chart(px.box(cycle, x="sales_channel", y="days_to_offer", color="sales_channel", title="Time from opportunity to offer"), width="stretch")


def care_page(data: dict[str, pd.DataFrame]) -> None:
    st.subheader("Customer Care Analysis")
    care = data["care"]
    if care.empty:
        st.info("No customer-care cases match the current filters.")
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Care cases", f"{len(care):,}")
    c2.metric("Average resolution time", f"{care.resolution_hours.mean():.1f} hours")
    c3.metric("Customer satisfaction", f"{care.satisfaction_score.mean():.1f}/5")
    left, right = st.columns(2)
    with left:
        categories = care.groupby("case_category", as_index=False).case_id.count().sort_values("case_id", ascending=False)
        st.plotly_chart(px.bar(categories, x="case_category", y="case_id", color_discrete_sequence=[PRIMARY], title="Cases by category"), width="stretch")
    with right:
        st.plotly_chart(px.scatter(care.dropna(subset=["resolution_hours"]), x="resolution_hours", y="satisfaction_score", color="contact_channel", title="Resolution time and satisfaction", labels={"resolution_hours": "Resolution hours", "satisfaction_score": "Satisfaction"}), width="stretch")


def loyalty_page(data: dict[str, pd.DataFrame]) -> None:
    st.subheader("Customer Loyalty Analysis")
    purchases = data["purchases"]
    initial = purchases[purchases.purchase_type == "Initial"]
    repeat = purchases[purchases.purchase_type == "Repeat"]
    rate = safe_divide(repeat.customer_id.nunique(), initial.customer_id.nunique())
    c1, c2, c3 = st.columns(3)
    c1.metric("Initial purchasers", f"{initial.customer_id.nunique():,}")
    c2.metric("Repeat purchasers", f"{repeat.customer_id.nunique():,}")
    c3.metric("Repeat-purchase rate", f"{rate:.1%}")
    repeat_product = repeat.groupby("product", as_index=False).customer_id.nunique().sort_values("customer_id", ascending=False)
    st.plotly_chart(px.bar(repeat_product, x="product", y="customer_id", color="product", title="Repeat purchasers by product").update_layout(showlegend=False), width="stretch")
    if not initial.empty and not repeat.empty:
        dates = initial[["customer_id", "purchase_date"]].rename(columns={"purchase_date": "initial_date"}).merge(repeat[["customer_id", "purchase_date"]].rename(columns={"purchase_date": "repeat_date"}), on="customer_id")
        dates["days_to_repeat"] = (dates.repeat_date - dates.initial_date).dt.days
        st.plotly_chart(px.histogram(dates, x="days_to_repeat", nbins=20, color_discrete_sequence=[PRIMARY], title="Time to repeat purchase"), width="stretch")


def main() -> None:
    st.title("Funnel Intelligence & Customer Journey Dashboard")
    if not DATA.exists():
        st.error("Processed data is missing. Run `python3 -m src.pipeline` first.")
        st.stop()
    data = apply_filters(load_data())
    if data["events"].empty:
        st.warning("No customer-journey records match the selected filters. Expand the reporting period or clear one or more filters.")
        st.stop()
    tabs = st.tabs(["Executive", "Funnel", "Marketing", "Sales", "Customer Care", "Loyalty"])
    with tabs[0]: executive_page(data)
    with tabs[1]: funnel_page(data)
    with tabs[2]: marketing_page(data)
    with tabs[3]: sales_page(data)
    with tabs[4]: care_page(data)
    with tabs[5]: loyalty_page(data)
    st.divider()
    st.download_button("Download filtered funnel events", data["events"].to_csv(index=False).encode("utf-8"), "filtered_funnel_events.csv", "text/csv")


if __name__ == "__main__":
    main()
