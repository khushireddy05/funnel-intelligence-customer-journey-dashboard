# Power BI Data Model

Use a star schema. Dimension tables filter fact tables through one-to-many, single-direction relationships.

| Fact table | Grain | Main relationships |
|---|---|---|
| FactFunnelEvents | One customer reaching one funnel stage | Customer ID, Product, Date, Funnel Stage |
| FactInteractions | One marketing/customer interaction | Customer ID, Interaction Date, Channel |
| FactLeads | One lead | Customer ID, Lead Date, Product |
| FactOpportunities | One sales opportunity | Customer ID, Opportunity Date, Product |
| FactPurchases | One completed purchase | Customer ID, Purchase Date, Product |
| FactCustomerCare | One service case | Customer ID, Opened Date |

## Core relationships

```text
DimCustomer (1) ── (*) all fact tables through customer_id
DimProduct  (1) ── (*) FunnelEvents, Leads, Opportunities, Purchases through product
DimDate     (1) ── (*) active relationship to the primary date in each fact table
DimFunnelStage (1) ── (*) FactFunnelEvents through stage
```

For the initial dashboard, use the active date relationship to `FactFunnelEvents[stage_date]`, `FactPurchases[purchase_date]`, and `FactCustomerCare[opened_date]`. Create inactive relationships or duplicated date dimensions only when a report needs secondary dates such as offer date or qualified date.
