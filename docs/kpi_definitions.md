# HirayaManawari: KPI Definitions

## Project Overview
Hiraya Manawari is a clothing online store selling on a Shopee/Lazada-style
marketplace in the Philippines. The owner feels sales are slow and wants
to understand the business. This project analyzes orders, customers, and
products to find what sells, where, and how customers pay.

## Business Questions and KPIs

| # | Business question | KPI |
|---|---|---|
| 1 | How much money are we making, and is it growing? | Total Revenue, MoM Growth % |
| 2 | How many orders do we get, and how big is each one? | Total Orders, Average Order Value (AOV) |
| 3 | What sells best? | Revenue by Category, Top 10 Products |
| 4 | Where are our customers? | Revenue by Region/City |
| 5 | How do people pay, and does it matter? | Orders by Payment Method |
| 6 | How many orders fail? | Cancellation Rate %, Return Rate % |
| 7 | Do customers come back? | Repeat Customer Rate % |
| 8 | Do big sale days work? | Revenue on 9.9 / 11.11 / 12.12 vs normal days |
| 9 | Which day of the week has the most orders? | Orders by Day of Week |

## KPI Formulas

- **Total Revenue** = sum of (price x quantity) for completed orders only
- **AOV** = Total Revenue / Number of Completed Orders
- **MoM Growth %** = (This Month - Last Month) / Last Month x 100
- **Cancellation Rate %** = Cancelled Orders / Total Orders x 100
- **Repeat Customer Rate % = Customers with 2+ orders / Customers with at least 1 order x 100

## Data Tables Needed

- **Orders:** order_id, customer_id, order_date, status, payment_method, shipping_fee
- **Order_Items:** order_id, product_id, quantity, unit_price
- **Customers:** customer_id, city, province, signup_date
- **Products:** product_id, product_name, category, price