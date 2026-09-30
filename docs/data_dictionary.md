# Data Dictionary

## Dimensions

| Table | Field | Meaning |
|---|---|---|
| DimCustomer | customer_id | Synthetic unique customer identifier |
| DimCustomer | customer_segment | Small Business, Fleet, Private, or Enterprise |
| DimCustomer | customer_type | New or Existing customer |
| DimCustomer | country / region | Customer geography |
| DimProduct | product | Demo vehicle name |
| DimProduct | product_category | Grouping of demo vehicle products |
| DimDate | date | Calendar date with reporting attributes |
| DimFunnelStage | stage / stage_order | Journey stage and its fixed order |

## Facts

| Table | Grain | Key fields |
|---|---|---|
| FactInteractions | One interaction | interaction date, channel, interaction type, campaign, stage |
| FactLeads | One lead | lead date, qualification date, lead source, status, product |
| FactOpportunities | One opportunity | opportunity date, offer date, sales channel, product, status |
| FactPurchases | One completed transaction | purchase date, product, purchase value, purchase type |
| FactCustomerCare | One service case | opened date, contact channel, category, resolution, satisfaction |
| FactFunnelEvents | One customer first reaching a stage | stage date, product, marketing channel, previous-stage duration |

All identifiers and all business records in this repository are synthetic.
