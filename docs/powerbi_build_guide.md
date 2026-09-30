# Power BI Build Guide

This guide turns the processed CSV output into a finished Power BI report. A `.pbix` cannot be authored in this environment because Power BI Desktop is Windows-only; all source data, relationship instructions, visual definitions, and DAX are included here.

## 1. Refresh the project data

From the project root, run:

```bash
python3 -m src.pipeline
python3 -m src.dashboard_artifacts
```

## 2. Import and transform

1. In Power BI Desktop, choose **Get data → Text/CSV** and import every file from `data/processed/`.
2. In Power Query, set identifiers and categories to Text; set dates to Date; set `purchase_value`, `resolution_hours`, and `satisfaction_score` to numeric types.
3. Disable automatic date/time tables in Power BI options.
4. Mark `DimDate[date]` as the model’s date table.
5. Use `powerbi/power_query_import.m` as the template for a parameterised import if the project will be refreshed regularly.

## 3. Relationships

Create the relationships specified in `docs/data_model.md`. Use one-to-many relationships from dimensions to facts and single-direction filtering. Do not join fact tables directly to one another.

## 4. Measures and formatting

Create the DAX measures in `powerbi/dax_measures.md`. Format conversion, repeat-purchase, and resolution measures as percentages; format revenue as euro currency; format durations as whole numbers; and format satisfaction to one decimal place.

## 5. Report pages

Build the six pages in `docs/dashboard_specification.md`. The preview in `images/dashboard_screenshots/executive_overview_preview.png` is the visual direction for the Executive Overview page.

Recommended styling:

- Background: `#F7F9FB`
- Primary: `#00A19A`
- Dark text: `#192A3A`
- Highlight / alert: `#F0A500`
- Keep KPI cards in the top row and use a consistent slicer panel.

## 6. Validate before publishing

Compare report totals with the generated insight report and the `Fact*` tables. In particular, confirm that initial prospects, initial purchasers, revenue, repeat purchasers, resolved cases, and satisfaction values reconcile. Test every global slicer on each dashboard page.
