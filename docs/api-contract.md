# Retail Sales Data Engineering Pipeline - API Contract Specification

This document defines the standardized HTTP API contract established between the **Frontend React/Next.js Application** and the **FastAPI Backend Data Engineering Service**.

The backend engineering team must implement these RESTful FastAPI endpoints to seamlessly replace the frontend MSW (Mock Service Worker) mock API layer.

---

## Global API Standards

### Base URL
- Development MSW Mock Base: `/api`
- Production FastAPI Base: `http://localhost:8000/api` (Configurable via `NEXT_PUBLIC_API_URL` environment variable).

### Response Wrappers

#### Standard Single Item Response
```json
{
  "data": { ... },
  "message": "Optional message string",
  "timestamp": "2025-09-18T14:30:00Z"
}
```

#### Standard Paginated Collection Response
```json
{
  "data": [ ... ],
  "meta": {
    "total": 145,
    "page": 1,
    "pageSize": 10,
    "totalPages": 15
  }
}
```

#### Standard Error Response Format
```json
{
  "message": "Resource not found or validation constraint failed",
  "code": "ERR_404",
  "details": {
    "field": "customer_id",
    "issue": "Foreign key constraint failure"
  }
}
```

---

## Endpoints Specification

### 1. Dashboard Overview
- **HTTP Method**: `GET`
- **Endpoint**: `/api/dashboard/summary`
- **Description**: Returns overall retail KPIs, chart trend data, recent stream transactions, low stock reorder alerts, and ingestion pipeline status.
- **Request Parameters**: None

#### Sample Response JSON (200 OK)
```json
{
  "data": {
    "totalRevenue": 248950.00,
    "revenueGrowthPercentage": 12.4,
    "totalOrders": 1845,
    "ordersGrowthPercentage": 8.2,
    "totalCustomers": 4120,
    "totalSkus": 145,
    "totalInventoryUnits": 38450,
    "lowStockItemsCount": 12,
    "salesTrend": [
      { "date": "Sep 01", "revenue": 6400, "orders": 48 },
      { "date": "Sep 02", "revenue": 7100, "orders": 52 }
    ],
    "salesByStore": [
      { "storeId": "STR-101", "storeName": "Downtown Flagship", "revenue": 84200, "orders": 580 }
    ],
    "topProducts": [
      { "skuId": "SKU-ELE-001", "productName": "Ultra-Slim Headphones", "category": "Electronics", "unitsSold": 210, "totalRevenue": 52497.90 }
    ],
    "salesByCategory": [
      { "category": "Electronics", "revenue": 98500, "percentage": 39.5 }
    ],
    "recentSales": [
      { "saleId": "SAL-9901", "date": "2025-09-18 14:32", "customerName": "Sarah Jenkins", "productName": "Ultra-Slim Headphones", "storeName": "Downtown Flagship", "totalAmount": 249.99 }
    ],
    "lowStockAlerts": [
      { "skuId": "SKU-ELE-002", "productName": "Smart Fitness Watch", "storeName": "Downtown Flagship", "stockOnHand": 4, "reorderPoint": 10 }
    ],
    "pipelineStatus": {
      "status": "HEALTHY",
      "lastRunAt": "2025-09-18T14:30:00Z",
      "recordsProcessedToday": 148520,
      "errorRatePercentage": 0.42
    }
  }
}
```

---

### 2. Sales Transactions List
- **HTTP Method**: `GET`
- **Endpoint**: `/api/sales`
- **Description**: Returns paginated sales transaction stream records with optional filtering by store, category, date range, or search string.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `pageSize` (int, default: 10)
  - `search` (string, optional)
  - `storeId` (string, optional, e.g. `STR-101`)
  - `category` (string, optional, e.g. `Electronics`)
  - `sortBy` (string, default: `saleDate`)
  - `sortOrder` (string, `asc` | `desc`, default: `desc`)

#### Sample Response JSON (200 OK)
```json
{
  "data": [
    {
      "saleId": "SAL-9901",
      "saleDate": "2025-09-18T14:32:00Z",
      "customerId": "CUST-1001",
      "customerName": "Sarah Jenkins",
      "skuId": "SKU-ELE-001",
      "productName": "Ultra-Slim Noise Cancelling Headphones",
      "category": "Electronics",
      "storeId": "STR-101",
      "storeName": "Downtown Flagship",
      "quantity": 1,
      "unitPrice": 249.99,
      "totalAmount": 249.99,
      "paymentMethod": "Credit Card"
    }
  ],
  "meta": {
    "total": 50,
    "page": 1,
    "pageSize": 10,
    "totalPages": 5
  }
}
```

---

### 3. Sales Aggregate Metrics
- **HTTP Method**: `GET`
- **Endpoint**: `/api/sales/metrics`
- **Description**: Returns total sales transaction metrics summary.

#### Sample Response JSON (200 OK)
```json
{
  "data": {
    "totalSalesCount": 1845,
    "totalRevenue": 248950.00,
    "averageOrderValue": 134.93,
    "totalQuantitySold": 3410
  }
}
```

---

### 4. Inventory Monitoring
- **HTTP Method**: `GET`
- **Endpoint**: `/api/inventory`
- **Description**: Returns paginated stock items across stores with reorder points and status indicators.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `pageSize` (int, default: 10)
  - `search` (string, optional)
  - `storeId` (string, optional)
  - `status` (string, optional: `IN_STOCK` | `LOW_STOCK` | `OUT_OF_STOCK`)

#### Sample Response JSON (200 OK)
```json
{
  "data": [
    {
      "id": "INV-101",
      "storeId": "STR-101",
      "storeName": "Downtown Flagship",
      "skuId": "SKU-ELE-001",
      "productName": "Ultra-Slim Noise Cancelling Headphones",
      "category": "Electronics",
      "stockOnHand": 42,
      "reorderPoint": 15,
      "status": "IN_STOCK",
      "lastRestocked": "2025-09-10"
    }
  ],
  "meta": {
    "total": 20,
    "page": 1,
    "pageSize": 10,
    "totalPages": 2
  }
}
```

---

### 5. Products Catalog (SKUs)
- **HTTP Method**: `GET`
- **Endpoint**: `/api/products`
- **Description**: Returns registered master SKUs.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `pageSize` (int, default: 10)
  - `search` (string, optional)
  - `category` (string, optional)
  - `status` (string, optional: `ACTIVE` | `DISCONTINUED` | `DRAFT`)

#### Sample Response JSON (200 OK)
```json
{
  "data": [
    {
      "skuId": "SKU-ELE-001",
      "productName": "Ultra-Slim Noise Cancelling Headphones",
      "category": "Electronics",
      "brand": "SoundPulse",
      "price": 249.99,
      "costPrice": 120.00,
      "unit": "piece",
      "status": "ACTIVE",
      "createdAt": "2025-01-15",
      "description": "High-fidelity Bluetooth wireless headphones with active noise cancellation."
    }
  ],
  "meta": {
    "total": 15,
    "page": 1,
    "pageSize": 10,
    "totalPages": 2
  }
}
```

---

### 6. Single Product Details
- **HTTP Method**: `GET`
- **Endpoint**: `/api/products/{skuId}`
- **Description**: Returns detailed SKU properties.

---

### 7. Customer Profiles Analytics
- **HTTP Method**: `GET`
- **Endpoint**: `/api/customers`
- **Description**: Returns customer profiles and aggregated purchase stats.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `pageSize` (int, default: 10)
  - `search` (string, optional)
  - `loyaltyTier` (string, optional: `PLATINUM` | `GOLD` | `SILVER` | `BRONZE`)

#### Sample Response JSON (200 OK)
```json
{
  "data": [
    {
      "customerId": "CUST-1001",
      "fullName": "Sarah Jenkins",
      "email": "s.jenkins@example.com",
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "totalPurchases": 2840.50,
      "totalOrders": 14,
      "loyaltyTier": "PLATINUM",
      "firstPurchasedAt": "2024-03-15",
      "lastPurchasedAt": "2025-09-12"
    }
  ],
  "meta": {
    "total": 10,
    "page": 1,
    "pageSize": 10,
    "totalPages": 1
  }
}
```

---

### 8. Promotions Management
- **HTTP Method**: `GET`
- **Endpoint**: `/api/promotions`
- **Description**: Returns promotional campaigns and redemption statistics.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `pageSize` (int, default: 10)
  - `status` (string, optional: `ACTIVE` | `UPCOMING` | `EXPIRED`)

---

### 9. Data Quality Summary
- **HTTP Method**: `GET`
- **Endpoint**: `/api/data-quality/summary`
- **Description**: Returns pipeline validation rule results (Schema, Null check, Duplicate check, Customer FK, SKU FK, Data Type validation) and total valid/invalid record counts.

#### Sample Response JSON (200 OK)
```json
{
  "data": {
    "pipelineStatus": "HEALTHY",
    "lastRunTimestamp": "2025-09-18T14:30:00Z",
    "totalRecordsProcessed": 148520,
    "totalValidRecords": 147890,
    "totalInvalidRecords": 630,
    "overallPassRate": 99.58,
    "categories": [
      {
        "category": "SCHEMA",
        "name": "Schema Validation",
        "description": "Checks JSON payload structures and mandatory headers.",
        "totalEvaluated": 148520,
        "passedCount": 148500,
        "failedCount": 20,
        "passRatePercentage": 99.98,
        "status": "PASSED"
      }
    ],
    "issuesCountBySeverity": {
      "critical": 465,
      "warning": 150,
      "info": 15
    }
  }
}
```

---

### 10. Data Quality Exception Issues Table
- **HTTP Method**: `GET`
- **Endpoint**: `/api/data-quality/issues`
- **Description**: Returns granular logs of rejected records and quarantine recommendations.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `pageSize` (int, default: 10)
  - `search` (string, optional)
  - `category` (string, optional: `SCHEMA` | `NULL_CHECK` | `DUPLICATE` | `CUSTOMER_FK` | `SKU_FK` | `DATA_TYPE`)
  - `severity` (string, optional: `CRITICAL` | `WARNING` | `INFO`)

#### Sample Response JSON (200 OK)
```json
{
  "data": [
    {
      "issueId": "DQ-ERR-8801",
      "timestamp": "2025-09-18T14:15:22Z",
      "category": "CUSTOMER_FK",
      "ruleViolated": "FOREIGN_KEY_EXISTS",
      "targetTable": "raw_sales",
      "targetColumn": "customer_id",
      "recordIdentifier": "RAW_TXN_99182",
      "severity": "CRITICAL",
      "invalidValue": "CUST-9999",
      "recommendation": "Orphan record detected. Route transaction to dead-letter quarantine table."
    }
  ],
  "meta": {
    "total": 6,
    "page": 1,
    "pageSize": 10,
    "totalPages": 1
  }
}
```
