# Industrial Funnel Intelligence Architecture

The [Eraser architecture DSL](industrial_funnel_architecture.eraser) documents the production-scale version of this portfolio project. It introduces resilient ingestion, customer identity resolution, governed lakehouse layers, privacy controls, certified BI metrics, operational analytics, ML activation, and observability.

## How to render it in Eraser

1. Sign in to [Eraser](https://app.eraser.io/).
2. Create a new file, choose **Diagram as Code**, then select **Architecture Diagram**.
3. Open `docs/industrial_funnel_architecture.eraser`, copy all content, and paste it into the Eraser editor.
4. Eraser will generate an editable grouped architecture diagram. Adjust layout only if desired.

## Architecture layers

| Layer | Responsibility |
|---|---|
| Source systems | Marketing, CRM, dealer, care, digital event, and master-data records |
| Integration and security | Secure APIs, streaming, batch imports, secrets, and enterprise identity |
| Data platform | Lakehouse ingestion, validation, identity matching, transformation, curated data, warehouse, and ML features |
| Governance and privacy | Data catalog, lineage, consent, retention, access enforcement, and audit evidence |
| Analytics and serving | Certified Power BI metrics, Streamlit investigation app, ML scoring, alerts, and CRM activation |
| Operations | CI/CD, infrastructure as code, monitoring, model monitoring, and incident management |

## Key industrial capabilities

- **Incremental and streaming ingestion:** only new or changed records are processed, while real-time digital events arrive through streaming.
- **Golden Customer ID:** customer identity resolution connects marketing, sales, dealer, vehicle, and care systems without relying on a single source identifier.
- **Medallion data design:** immutable raw data is preserved in Bronze; conformed, quality-checked events in Silver; reusable facts, dimensions, and aggregates in Gold.
- **Governed metrics:** Power BI uses a certified semantic model so conversion, satisfaction, revenue, and retention are calculated consistently.
- **Closed-loop actions:** a poor conversion rate or a high churn-risk score can create a CRM action, campaign audience, or alert—not merely a dashboard observation.
- **Production resilience:** orchestration, data-quality monitoring, lineage, access controls, audit logs, CI/CD, and incident management ensure the platform is reliable and compliant.
