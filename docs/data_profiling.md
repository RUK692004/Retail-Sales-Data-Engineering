# Processed Data Profiling Report

This report summarizes the structure and data quality of the processed retail datasets before transformation.

**Datasets profiled:** 6

## customers_ingested.csv

### Dataset Overview

- **Rows:** 5000
- **Columns:** 7
- **Duplicate rows:** 0

### Column Information

| Column            | Data Type   |   Null Count |   Null % |   Unique Values |
|:------------------|:------------|-------------:|---------:|----------------:|
| cust_id           | int64       |            0 |        0 |            5000 |
| age               | int64       |            0 |        0 |              10 |
| gender            | object      |            0 |        0 |               2 |
| city              | object      |            0 |        0 |               3 |
| loyalty_segment   | object      |            0 |        0 |               3 |
| preferred_channel | object      |            0 |        0 |               5 |
| registration_date | object      |            0 |        0 |            1675 |

### Numeric Summary

|         |   count |   mean |     std |   min |     25% |    50% |     75% |   max |
|:--------|--------:|-------:|--------:|------:|--------:|-------:|--------:|------:|
| cust_id |    5000 | 2500.5 | 1443.52 |     1 | 1250.75 | 2500.5 | 3750.25 |  5000 |
| age     |    5000 |   31.1 |   10.75 |    18 |   20    |   30   |   35    |    60 |

### Missing Values

No missing values found.

### Sample Records

|   cust_id |   age | gender   | city      | loyalty_segment   | preferred_channel   | registration_date   |
|----------:|------:|:---------|:----------|:------------------|:--------------------|:--------------------|
|         1 |    50 | Male     | Sharjah   | Silver            | MobileApp           | 2024-06-29          |
|         2 |    20 | Female   | Abu Dhabi | Gold              | Store               | 2024-12-03          |
|         3 |    55 | Male     | Dubai     | Gold              | Website             | 2023-09-18          |
|         4 |    25 | Male     | Abu Dhabi | Platinum          | Store               | 2022-01-02          |
|         5 |    20 | Female   | Abu Dhabi | Silver            | MobileApp           | 2021-09-13          |

## inventory_ingested.csv

### Dataset Overview

- **Rows:** 8735
- **Columns:** 7
- **Duplicate rows:** 0

### Column Information

| Column            | Data Type   |   Null Count |   Null % |   Unique Values |
|:------------------|:------------|-------------:|---------:|----------------:|
| store_id          | int64       |            0 |        0 |              50 |
| sku_id            | int64       |            0 |        0 |             200 |
| stock_on_hand     | int64       |            0 |        0 |             398 |
| reorder_point     | int64       |            0 |        0 |             189 |
| safety_stock      | int64       |            0 |        0 |             100 |
| last_restock_date | object      |            0 |        0 |              89 |
| snapshot_date     | object      |            0 |        0 |               1 |

### Numeric Summary

|               |   count |    mean |   std |   min |   25% |   50% |   75% |   max |
|:--------------|--------:|--------:|------:|------:|------:|------:|------:|------:|
| store_id      |    8735 |   25.34 | 14.39 |     1 |    13 |    25 |    38 |    50 |
| sku_id        |    8735 | 1100.3  | 57.63 |  1001 |  1051 |  1100 |  1150 |  1200 |
| stock_on_hand |    8735 |  170.76 | 77.88 |    35 |   112 |   156 |   217 |   449 |
| reorder_point |    8735 |   67.76 | 32.99 |    10 |    43 |    62 |    87 |   217 |
| safety_stock  |    8735 |   33.63 | 16.5  |     5 |    21 |    31 |    43 |   108 |

### Missing Values

No missing values found.

### Sample Records

|   store_id |   sku_id |   stock_on_hand |   reorder_point |   safety_stock | last_restock_date   | snapshot_date   |
|-----------:|---------:|----------------:|----------------:|---------------:|:--------------------|:----------------|
|          9 |     1101 |             300 |              92 |             46 | 2025-10-18          | 2025-10-31      |
|          9 |     1021 |             425 |             162 |             81 | 2025-10-21          | 2025-10-31      |
|          9 |     1200 |             252 |              85 |             42 | 2025-09-14          | 2025-10-31      |
|          9 |     1041 |             220 |              87 |             43 | 2025-10-13          | 2025-10-31      |
|          9 |     1092 |             170 |              80 |             40 | 2025-09-12          | 2025-10-31      |

## promotions_ingested.csv

### Dataset Overview

- **Rows:** 33
- **Columns:** 6
- **Duplicate rows:** 0

### Column Information

| Column       | Data Type   |   Null Count |   Null % |   Unique Values |
|:-------------|:------------|-------------:|---------:|----------------:|
| promo_name   | object      |            0 |        0 |              33 |
| start_date   | object      |            0 |        0 |              33 |
| end_date     | object      |            0 |        0 |              33 |
| discount_pct | int64       |            0 |        0 |               6 |
| promo_type   | object      |            0 |        0 |               6 |
| promo_id     | int64       |            0 |        0 |              33 |

### Numeric Summary

|              |   count |   mean |   std |   min |   25% |   50% |   75% |   max |
|:-------------|--------:|-------:|------:|------:|------:|------:|------:|------:|
| discount_pct |      33 |  21.21 |  7.71 |    10 |    15 |    20 |    25 |    35 |
| promo_id     |      33 |  17    |  9.67 |     1 |     9 |    17 |    25 |    33 |

### Missing Values

No missing values found.

### Sample Records

| promo_name                   | start_date   | end_date   |   discount_pct | promo_type   |   promo_id |
|:-----------------------------|:-------------|:-----------|---------------:|:-------------|-----------:|
| Ramadan Sale 2021            | 2021-04-13   | 2021-05-12 |             25 | Ramadan      |          1 |
| Eid Al Fitr Sale 2021        | 2021-05-13   | 2021-05-15 |             20 | Eid          |          2 |
| Eid Al Adha Sale 2021        | 2021-07-20   | 2021-07-22 |             25 | Eid          |          3 |
| Dubai Shopping Festival 2021 | 2021-01-01   | 2021-02-28 |             15 | DSF          |          4 |
| Black Friday 2021            | 2021-11-26   | 2021-11-28 |             30 | Black Friday |          5 |

## sales_ingested.csv

### Dataset Overview

- **Rows:** 641843
- **Columns:** 9
- **Duplicate rows:** 45

### Column Information

| Column       | Data Type   |   Null Count |   Null % |   Unique Values |
|:-------------|:------------|-------------:|---------:|----------------:|
| date         | object      |            0 |      0   |            1765 |
| store_id     | int64       |            0 |      0   |              50 |
| sku_id       | int64       |            0 |      0   |             200 |
| customer_id  | float64     |       159821 |     24.9 |            5000 |
| quantity     | int64       |            0 |      0   |               6 |
| unit_price   | float64     |            0 |      0   |            1227 |
| total_value  | float64     |            0 |      0   |            6062 |
| channel      | object      |            0 |      0   |               5 |
| discount_pct | float64     |            0 |      0   |               7 |

### Numeric Summary

|              |   count |    mean |     std |    min |     25% |     50% |     75% |     max |
|:-------------|--------:|--------:|--------:|-------:|--------:|--------:|--------:|--------:|
| store_id     |  641843 |   25.49 |   14.44 |    1   |   13    |   25    |   38    |   50    |
| sku_id       |  641843 | 1100.55 |   57.68 | 1001   | 1051    | 1101    | 1150    | 1200    |
| customer_id  |  482022 | 2504.99 | 1442.34 |    1   | 1260    | 2507    | 3752    | 5000    |
| quantity     |  641843 |    2.61 |    1.48 |    1   |    1    |    2    |    4    |    6    |
| unit_price   |  641843 |   44.11 |   48.98 |    1.7 |   14.28 |   24.33 |   49.57 |  245.38 |
| total_value  |  641843 |  114.07 |  157.21 |    1.7 |   27.32 |   57.66 |  129.55 | 1472.28 |
| discount_pct |  641843 |    5.41 |    8.66 |    0   |    0    |    0    |   10    |   35    |

### Missing Values

| Column | Missing Count | Missing % |
|---|---:|---:|
| customer_id | 159821 | 24.90% |

### Sample Records

| date       |   store_id |   sku_id |   customer_id |   quantity |   unit_price |   total_value | channel   |   discount_pct |
|:-----------|-----------:|---------:|--------------:|-----------:|-------------:|--------------:|:----------|---------------:|
| 2021-01-01 |         26 |     1124 |          2961 |          1 |        20.08 |         20.08 | Store     |             15 |
| 2021-01-01 |         19 |     1035 |           nan |          3 |       208.57 |        625.71 | Store     |             15 |
| 2021-01-01 |         38 |     1088 |           nan |          1 |        17.99 |         17.99 | Website   |             15 |
| 2021-01-01 |          3 |     1164 |          3694 |          6 |       196.24 |       1177.44 | Website   |              0 |
| 2021-01-01 |          2 |     1093 |          1252 |          1 |         7.98 |          7.98 | Store     |              0 |

## skus_ingested.csv

### Dataset Overview

- **Rows:** 200
- **Columns:** 7
- **Duplicate rows:** 0

### Column Information

| Column      | Data Type   |   Null Count |   Null % |   Unique Values |
|:------------|:------------|-------------:|---------:|----------------:|
| sku_id      | int64       |            0 |        0 |             200 |
| sku_name    | object      |            0 |        0 |             200 |
| category    | object      |            0 |        0 |               7 |
| subcategory | object      |            0 |        0 |              33 |
| unit_price  | float64     |            0 |        0 |             196 |
| cost_price  | float64     |            0 |        0 |             196 |
| brand       | object      |            0 |        0 |               5 |

### Numeric Summary

|            |   count |    mean |   std |     min |     25% |     50% |     75% |     max |
|:-----------|--------:|--------:|------:|--------:|--------:|--------:|--------:|--------:|
| sku_id     |     200 | 1100.5  | 57.88 | 1001    | 1050.75 | 1100.5  | 1150.25 | 1200    |
| unit_price |     200 |   46.68 | 51.59 |    2.61 |   15.24 |   25.91 |   51.27 |  245.38 |
| cost_price |     200 |   31.06 | 34.44 |    1.68 |   10.07 |   17.12 |   34.32 |  187.67 |

### Missing Values

No missing values found.

### Sample Records

|   sku_id | sku_name                         | category    | subcategory       |   unit_price |   cost_price | brand         |
|---------:|:---------------------------------|:------------|:------------------|-------------:|-------------:|:--------------|
|     1001 | Electronics_Chargers_1001        | Electronics | Chargers          |       164.56 |       103.44 | Budget        |
|     1002 | Dairy_Cream_1002                 | Dairy       | Cream             |        13.73 |         8.96 | Local         |
|     1003 | Household_Cleaning Supplies_1003 | Household   | Cleaning Supplies |        12    |         7.47 | BlueMart      |
|     1004 | Beverages_Juices_1004            | Beverages   | Juices            |        24.82 |        17.58 | International |
|     1005 | Household_Paper Products_1005    | Household   | Paper Products    |        17.7  |        13.68 | Budget        |

## stores_ingested.csv

### Dataset Overview

- **Rows:** 50
- **Columns:** 5
- **Duplicate rows:** 0

### Column Information

| Column       | Data Type   |   Null Count |   Null % |   Unique Values |
|:-------------|:------------|-------------:|---------:|----------------:|
| store_id     | int64       |            0 |        0 |              50 |
| store_name   | object      |            0 |        0 |              50 |
| city         | object      |            0 |        0 |               3 |
| store_type   | object      |            0 |        0 |               3 |
| opening_date | object      |            0 |        0 |              50 |

### Numeric Summary

|          |   count |   mean |   std |   min |   25% |   50% |   75% |   max |
|:---------|--------:|-------:|------:|------:|------:|------:|------:|------:|
| store_id |      50 |   25.5 | 14.58 |     1 | 13.25 |  25.5 | 37.75 |    50 |

### Missing Values

No missing values found.

### Sample Records

|   store_id | store_name        | city      | store_type   | opening_date                  |
|-----------:|:------------------|:----------|:-------------|:------------------------------|
|          9 | BlueMart Store 09 | Abu Dhabi | Mall         | 2017-01-01 00:00:00.000000000 |
|         10 | BlueMart Store 10 | Abu Dhabi | Mall         | 2017-01-31 00:00:00.000000000 |
|         11 | BlueMart Store 11 | Dubai     | Mall         | 2017-03-02 00:00:00.000000000 |
|         12 | BlueMart Store 12 | Sharjah   | Mall         | 2017-04-01 00:00:00.000000000 |
|         13 | BlueMart Store 13 | Sharjah   | Community    | 2017-05-01 00:00:00.000000000 |
