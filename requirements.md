# Refined Requirements

## Business goal

Provide an end-to-end view of synthetic customer acquisition and retention so Marketing, Sales, Customer Care, and Management can identify where performance is strong, where customers drop off, and which actions merit investigation.

## Official journey definitions

```text
Acquisition: Initial Interaction → Engaged Prospect → Lead → Qualified Lead
             → Opportunity → Offer → Purchase

Lifecycle:   Purchase → Customer Care / Satisfaction → Repeat Purchase
```

Customer care is a post-purchase activity, not a mandatory acquisition stage.

## Functional scope

- Generate synthetic, non-confidential source-system data for customers, interactions, leads, opportunities, purchases, and service cases.
- Validate data integrity before publishing analytical tables.
- Join events through a unique `customer_id`.
- Produce Power BI-ready fact and dimension CSVs.
- Measure funnel volume, conversion, drop-off, progression speed, revenue, satisfaction, service performance, and repeat purchasing.
- Support filtering by date, geography, product, segment, customer type, and channel.
- Provide six dashboard views: executive, funnel, marketing, sales, customer care, and loyalty.

## Acceptance criteria

- Pipeline runs from one documented command.
- Critical-quality checks must be zero before data is published.
- Fact tables retain event-level detail; KPI definitions use distinct customers where stated.
- Dashboard totals reconcile to processed data.
- Synthetic/demo status and business assumptions are documented.

## Out of scope for version 1

- Real customer data or any confidential Mercedes-Benz data.
- Automated cloud deployment or refresh.
- Predictive lead scoring, churn prediction, or customer lifetime value.
- Marketing cost metrics; source data does not yet contain spend.
