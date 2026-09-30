# Core DAX Measures

Replace table and column names only if Power BI changes them during import.

```DAX
Total Prospects =
CALCULATE(
    DISTINCTCOUNT(FactFunnelEvents[customer_id]),
    FactFunnelEvents[stage] = "Initial Interaction"
)

Total Leads =
CALCULATE(
    DISTINCTCOUNT(FactFunnelEvents[customer_id]),
    FactFunnelEvents[stage] = "Lead"
)

Qualified Leads =
CALCULATE(
    DISTINCTCOUNT(FactFunnelEvents[customer_id]),
    FactFunnelEvents[stage] = "Qualified Lead"
)

Initial Purchasers =
CALCULATE(
    DISTINCTCOUNT(FactPurchases[customer_id]),
    FactPurchases[purchase_type] = "Initial"
)

Purchase Revenue = SUM(FactPurchases[purchase_value])

Overall Conversion Rate = DIVIDE([Initial Purchasers], [Total Prospects])

Repeat Purchasers =
CALCULATE(
    DISTINCTCOUNT(FactPurchases[customer_id]),
    FactPurchases[purchase_type] = "Repeat"
)

Repeat Purchase Rate = DIVIDE([Repeat Purchasers], [Initial Purchasers])

Resolved Cases =
CALCULATE(COUNTROWS(FactCustomerCare), FactCustomerCare[resolution_status] = "Resolved")

Resolution Rate = DIVIDE([Resolved Cases], COUNTROWS(FactCustomerCare))

Average Resolution Hours =
AVERAGE(FactCustomerCare[resolution_hours])

Customer Satisfaction =
AVERAGE(FactCustomerCare[satisfaction_score])

Average Days Between Stages =
AVERAGE(FactFunnelEvents[days_from_previous_stage])
```

For a stage-conversion visual, place `DimFunnelStage[stage]` on rows and use a distinct count of `FactFunnelEvents[customer_id]`. Calculate comparisons to the preceding stage with a dedicated measure after the final model is loaded.
