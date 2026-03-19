from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

#DATA 

items = [
    {"id": 1, "name": "Milk", "price": 40, "unit": "litre", "category": "Dairy", "in_stock": True},
    {"id": 2, "name": "Rice", "price": 60, "unit": "kg", "category": "Grain", "in_stock": True},
    {"id": 3, "name": "Apple", "price": 120, "unit": "kg", "category": "Fruit", "in_stock": True},
    {"id": 4, "name": "Potato", "price": 30, "unit": "kg", "category": "Vegetable", "in_stock": False},
    {"id": 5, "name": "Eggs", "price": 70, "unit": "dozen", "category": "Dairy", "in_stock": True},
    {"id": 6, "name": "Tomato", "price": 25, "unit": "kg", "category": "Vegetable", "in_stock": True}
]

orders = []
cart = []

#MODELS 

class Order(BaseModel):
    customer_name: str
    item_id: int
    quantity: int
    delivery_address: str
    delivery_slot: str

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str
    delivery_slot: str

class UpdateOrder(BaseModel):
    customer_name: Optional[str] = None
    quantity: Optional[int] = None

#HELPER 

def find_item(item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    return None

# BASIC

@app.get("/")
def home():
    return {"message": "Welcome to FreshMart Grocery"}

@app.get("/items")
def get_items():
    return {"items": items, "total": len(items)}

#SEARCH

@app.get("/items/search")
def search_items(keyword: str):
    result = [i for i in items if keyword.lower() in i["name"].lower() or keyword.lower() in i["category"].lower()]
    return {"items": result, "total_found": len(result)}

# SORT

@app.get("/items/sort")
def sort_items(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name", "category"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by")
    sorted_items = sorted(items, key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"items": sorted_items}

# PAGINATION

@app.get("/items/page")
def paginate_items(page: int = 1, limit: int = 4):
    total = len(items)
    total_pages = (total + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    return {
        "items": items[start:end],
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

#BROWSE 

@app.get("/items/browse")
def browse_items(
    keyword: str = None,
    category: str = None,
    in_stock: bool = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = items

    if keyword:
        result = [i for i in result if keyword.lower() in i["name"].lower() or keyword.lower() in i["category"].lower()]

    if category:
        result = [i for i in result if i["category"].lower() == category.lower()]

    if in_stock is not None:
        result = [i for i in result if i["in_stock"] == in_stock]

    if sort_by not in ["price", "name", "category"]:
        sort_by = "price"

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    total = len(result)
    total_pages = (total + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit

    return {
        "results": result[start:end],
        "total_found": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

#GET ITEM (ALWAYS LAST)

@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# ORDERS

@app.post("/orders")
def create_order(order: Order):
    item = find_item(order.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    total = item["price"] * order.quantity

    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": order.customer_name,
        "item": item["name"],
        "quantity": order.quantity,
        "total_cost": total
    }

    orders.append(new_order)
    return new_order

@app.get("/orders/search")
def search_orders(query: str):
    result = [o for o in orders if query.lower() in o["customer_name"].lower()]
    return result if result else {"message": "No orders found"}

@app.get("/orders/sort")
def sort_orders(order: str = "asc"):
    return sorted(orders, key=lambda x: x["total_cost"], reverse=(order == "desc"))

@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return orders[start:start+limit]

#CART

@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int = 1):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return {"cart": cart}

    cart.append({
        "item_id": item_id,
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity
    })

    return {"cart": cart}

@app.get("/cart")
def view_cart():
    total = 0
    result = []
    for c in cart:
        subtotal = c["price"] * c["quantity"]
        total += subtotal
        result.append({**c, "subtotal": subtotal})
    return {"cart": result, "grand_total": total}

@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int):
    for c in cart:
        if c["item_id"] == item_id:
            cart.remove(c)
            return {"message": "Item removed", "cart": cart}
    raise HTTPException(status_code=404, detail="Item not found in cart")

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    placed_orders = []
    total = 0

    for c in cart:
        cost = c["price"] * c["quantity"]
        total += cost

        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "item": c["name"],
            "quantity": c["quantity"],
            "total_cost": cost
        }

        orders.append(order)
        placed_orders.append(order)

    cart.clear()

    return {
        "orders": placed_orders,
        "grand_total": total
    }
