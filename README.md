#  Grocery API (FastAPI)

##  Overview

This project is a REST API built using FastAPI for managing grocery items, cart, and orders.
It includes operations like search, filter, sorting, pagination, and checkout.

---

##  Features (Q1–Q20)

* View all items & item by ID
* Filter items (category, price, stock)
* Search items (name & category)
* Sort items (price, name, category)
* Pagination (items & orders)
* Cart management (add, remove, view)
* Checkout system (place multiple orders)
* Order management (create, search, sort, delete)
* Combined browse (search + filter + sort + pagination)

---

## Tech Stack

* Python
* FastAPI
* Uvicorn

---

##  Run Project

bash
uvicorn main:app --reload
Open:
http://127.0.0.1:8000/docs
## APIs

### Items

* GET /items
* GET /items/{item_id}
* GET /items/search
* GET /items/sort
* GET /items/page
* GET /items/browse

### Cart

* POST /cart/add
* GET /cart
* DELETE /cart/{item_id}
* POST /cart/checkout

### Orders

* POST /orders
* GET /orders/search
* GET /orders/sort
* GET /orders/page

---
## 📸 Screenshots

All screenshots from **Q1 to Q20** are included in the repository.

---

##  Status

All Q1–Q20 implemented and tested successfully
