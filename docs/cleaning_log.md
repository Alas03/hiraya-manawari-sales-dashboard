# Cleaning Log

Every problem found in the raw data and how it was fixed.

| Table | Issue | Rows affected | Fix |
|---|---|---:|---|
| orders | Duplicate orders | 150 | Removed duplicate rows, kept first copy |
| orders | Mixed date formats | 2,421 | Parsed 3 formats into one YYYY-MM-DD date |
| orders | Inconsistent status casing | 1,000 | Trimmed spaces and applied Title Case |
| orders | Missing payment_method | 300 | Filled with 'Unknown' |
| customers | Inconsistent city names | 1,422 | Trimmed, lower-cased, then mapped to one official spelling (QC -> Quezon City) |
| customers | Missing province | 150 | Recovered from the customer's city |
| products | Inconsistent category text | 16 | Trimmed spaces and applied Title Case |
| order_items | Zero or negative unit_price | 40 | Replaced with the product's list price (sale discount unknown for these rows) |
