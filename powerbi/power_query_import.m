// Change FolderPath to the absolute path of the project's data/processed folder.
// Create a blank query named FolderPath that returns this text value, then create
// a new blank query for each CSV using the corresponding pattern below.

// Example: DimCustomer
let
    Source = Csv.Document(File.Contents(FolderPath & "DimCustomer.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(PromotedHeaders, {{"customer_id", type text}, {"customer_segment", type text}, {"customer_type", type text}, {"country", type text}, {"region", type text}, {"first_seen_date", type date}})
in
    Typed

// Import the other processed CSVs with Get Data → Text/CSV. Set all IDs and
// descriptive fields to Text, amounts/durations to Decimal or Whole Number, and
// all date fields to Date. Do not use automatic relationship detection.
