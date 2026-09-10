# Data Dictionary

## Pharmaceutical market

| Field | Type | Definition |
|---|---|---|
| `Month` | datetime | Month-start observation date. |
| `Brand_Name` | string | Synthetic commercial segment keyed to a real GLP-1 brand name. |
| `Manufacturer` | string | Brand manufacturer. |
| `Molecule` | string | Active molecule family. |
| `TRx` | integer | Synthetic total prescriptions for the month. |
| `NRx` | integer | Synthetic new prescriptions for the month. |
| `Average_Wholesale_Price_USD` | float | Synthetic AWP-like price assumption; not a reported net price. |
| `Gross_Revenue_USD` | float | Synthetic gross commercial value derived from TRx, price, and a gross-to-AWP factor. |

## Companion medical nutrition market

| Field | Type | Definition |
|---|---|---|
| `Month` | datetime | Month-start observation date. |
| `Supplement_Category` | string | Synthetic companion-nutrition category. |
| `Units_Sold` | integer | Synthetic monthly units sold. |
| `Average_Retail_Price_USD` | float | Synthetic average retail price. |
| `Total_Sales_USD` | float | Synthetic units multiplied by average retail price. |

## Unified analytical fact table

| Field | Type | Definition |
|---|---|---|
| `Month` | datetime | Month-start observation date. |
| `Market` | string | Pharmaceutical Prescriptions or Companion Medical Nutrition. |
| `Segment_Type` | string | Brand or Supplement Category. |
| `Segment` | string | Brand/category name. |
| `Manufacturer` | string/null | Manufacturer for pharmaceutical rows. |
| `Molecule` | string/null | Molecule for pharmaceutical rows. |
| `Volume` | numeric | TRx for pharma or Units Sold for nutrition. |
| `New_Volume` | numeric/null | NRx for pharma; null for nutrition. |
| `Price_USD` | float | AWP-like price for pharma or retail price for nutrition. |
| `Revenue_USD` | float | Gross pharma value or nutrition sales. |
