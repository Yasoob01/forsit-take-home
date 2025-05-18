# Retail Sales Analytics API

This project is a FastAPI-based application that provides a comprehensive API for managing retail sales data, inventory, and products across multiple platforms. It allows for tracking sales, analyzing revenue trends, managing inventory levels, and more.

---

## Features

- **Product Management**: Create, read, update, and delete products and categories
- **Inventory Management**: Track product inventory levels with low stock alerts
- **Sales Tracking**: Record and query sales data across different platforms
- **Analytics**: Generate insights on sales performance including:
  - Revenue by time period (daily, weekly, monthly, yearly)
  - Sales summary statistics
  - Platform-specific performance
  - Top-selling products
  - Period-over-period comparisons

---

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy ORM with SQL database
- **Data Models**: Pydantic schemas for request/response validation

## Installation

To set up the Retail Sales Analytics API, follow these steps:

### Clone the repository:

```bash
git clone https://github.com/yourusername/forsit-take-home.git
cd forsit-take-home
```

**Create and activate a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Set up environment variables:

Create a `.env` file in the project root with:

```bash
DATABASE_URL=postgresql://postgres:password@localhost/ecommerce_admin
```

### Create the PostgreSQL database:

```bash
psql -U postgres -c "CREATE DATABASE ecommerce_admin;"
```

### Generate demo data:

```bash
python demo_data.py
```

### Run the application:

```bash
uvicorn app.main:app --reload
```

---

## API Testing

You can test the API endpoints using curl commands/postman or browser:

```bash
# Get all products
curl -X GET "http://localhost:8000/products/" -H "accept: application/json"

# Get inventory status
curl -X GET "http://localhost:8000/inventory/" -H "accept: application/json"

# Get sales analytics summary
curl -X GET "http://localhost:8000/sales/analytics/summary" -H "accept: application/json"

# Get revenue by period
curl -X GET "http://localhost:8000/sales/analytics/revenue?period_type=monthly" -H "accept: application/json"

# Compare revenue between periods
curl -X GET "http://localhost:8000/sales/analytics/compare?period_type=monthly&current_start=2025-04-01&current_end=2025-04-30&previous_start=2025-03-01&previous_end=2025-03-30" -H "accept: application/json"

#Low stock Alerts
curl -X GET "http://localhost:8000/inventory/low-stock/alerts" -H "accept: application/json"
```

---

## Data Models:

### Category (Represents product categories):

| Column      | Type        | Description                    |
| ----------- | ----------- | ------------------------------ |
| id          | Integer     | Primary key                    |
| name        | String(100) | Unique category name (indexed) |
| description | Text        | Optional description           |

**Relationships:**

1. One-to-Many with Product

---

### Product (Represents items available for sale):

| Column      | Type         | Description                        |
| ----------- | ------------ | ---------------------------------- |
| id          | Integer      | Primary key                        |
| name        | String(200)  | Product name (indexed)             |
| description | Text         | Detailed description               |
| price       | Float        | Product price (non-nullable)       |
| sku         | String(50)   | Unique inventory identifier        |
| category_id | Integer (FK) | Foreign key to `categories`table |
| created_at  | DateTime     | Creation timestamp                 |
| updated_at  | DateTime     | Last update timestamp              |

**Relationships:**

* Many-to-One with Category
* One-to-One with Inventory
* One-to-Many with SaleItem

---

### Inventory (Tracks product stock levels):

| Column              | Type         | Description                         |
| ------------------- | ------------ | ----------------------------------- |
| id                  | Integer      | Primary key                         |
| product_id          | Integer (FK) | Foreign key to `products`(unique) |
| quantity            | Integer      | Current stock quantity              |
| low_stock_threshold | Integer      | Alert threshold (default: 10)       |
| last_restock_date   | DateTime     | Last restock date                   |
| created_at          | DateTime     | Creation timestamp                  |
| updated_at          | DateTime     | Last update timestamp               |

**Relationships:**

* One-to-One with Product
* One-to-Many with InventoryHistory

---

### InventoryHistory (Tracks inventory changes over time):

| Column            | Type         | Description                  |
| ----------------- | ------------ | ---------------------------- |
| id                | Integer      | Primary key                  |
| inventory_id      | Integer (FK) | Foreign key to `inventory` |
| previous_quantity | Integer      | Quantity before change       |
| new_quantity      | Integer      | Quantity after change        |
| change_date       | DateTime     | Timestamp of change          |
| change_reason     | String(200)  | Optional reason              |
| created_at        | DateTime     | Creation timestamp           |
| updated_at        | DateTime     | Last update timestamp        |

**Relationships:**

* Many-to-One with Inventory

### Sale (Represents customer orders):

| Column       | Type       | Description                       |
| ------------ | ---------- | --------------------------------- |
| id           | Integer    | Primary key                       |
| order_id     | String(50) | Unique order ID (indexed)         |
| order_date   | DateTime   | Order date/time                   |
| customer_id  | String(50) | Customer ID (indexed)             |
| total_amount | Float      | Total order amount (non-nullable) |
| platform     | String(50) | Sales platform (e.g., Amazon)     |
| status       | String(20) | Order status (default: "pending") |
| created_at   | DateTime   | Creation timestamp                |
| updated_at   | DateTime   | Last update timestamp             |

**Relationships:**

* One-to-Many with SaleItem

---

### SaleItem (Represents items within a sale):

| Column     | Type         | Description                          |
| ---------- | ------------ | ------------------------------------ |
| id         | Integer      | Primary key                          |
| sale_id    | Integer (FK) | Foreign key to `sales`             |
| product_id | Integer (FK) | Foreign key to `products`          |
| quantity   | Integer      | Quantity sold                        |
| unit_price | Float        | Price per unit at sale time          |
| subtotal   | Float        | Total price (quantity × unit_price) |
| created_at | DateTime     | Creation timestamp                   |
| updated_at | DateTime     | Last update timestamp                |

**Relationships:**

* Many-to-One with Sale
* Many-to-One with Product

---



## Schema Models

### Sales Schemas

* **SaleItemBase** : `product_id`, `quantity`, `unit_price`, `subtotal`
* **SaleItemCreate** : Schema for creating sale items
* **SaleItemInDB** : Retrieved sale item schema
* **SaleBase** : `order_id`, `order_date`, `customer_id`, `total_amount`, `platform`, `status`
* **SaleCreate** : Includes sale items
* **SaleInDB** : Sale record from DB
* **Sale** : Full sale schema with items

---



### Analytics Schemas

* **PeriodInfo** : Date range schema
* **SummaryInfo** : Sales statistics
* **PlatformSales** : Platform-specific data
* **TopProduct** : Top-selling product info
* **SalesAnalytics** : Complete analytics report
* **RevenueByPeriod** : Revenue grouped by time

---



### Inventory Schemas

* **InventoryBase** : `product_id`, `quantity`, `low_stock_threshold`
* **InventoryCreate** : New inventory record schema
* **InventoryInDB** : Inventory record from DB
* **InventoryHistoryBase** : Base schema for inventory change logs
* **InventoryHistoryCreate** : New history record schema
* **InventoryHistoryInDB** : Inventory history from DB
