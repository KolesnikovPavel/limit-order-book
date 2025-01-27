# Limit Order Book

This repository contains an implementation of a limit order book 
for a matching buy and sell orders. 

## Overview

A limit order book maintaining two main queues:
- Buy orders
- Sell orders

Each order includes:

- Order ID (order_id): A unique string identifier
- Side (side): "buy" or "sell"
- Price (price): The limit price
- Quantity (quantity): Number of units to be traded

## Matching Criteria
1. **Buy vs. Sell:** A buy order matches with a sell order if `buy_price >= sell_price`.
2. **Best Price / Earliest Time:**
   - For buys, highest price is matched first.
   - For sells, lowest price is matched first.
   - Among orders at the same price, the earliest one placed is matched first (in practice, Python’s heapq and an internal ordering handle this priority).

## Data Structures and Logic

The main components of the engine:

1. `Order` Class.
Holds basic attributes: `order_id`, `side`, `price`, `quantity`. It also defines a custom `__lt__` method to ensure correct priority in a heap:

   - For buy orders, higher prices should come out first (max-heap).
   - For sell orders, lower prices should come out first (min-heap).

2. `OrderBook` Class

   - `active_orders`: A dictionary mapping order_id → Order for all currently active orders.
   - `filled_orders`: A set tracking IDs of orders that have been completely filled.
   - `heap_buy_orders` and `heap_sell_orders`: Two heaps for matching buy and sell orders, respectively.

### Matching Mechanism
- **Heap Operations:**
In Python, `heapq` implements a min-heap. This engine overrides `__lt__` in `Order` to simulate a max-heap for buys and a min-heap for sells.
- **Loop Until No Match:**
When a new order arrives, the `_process_order` method repeatedly pops the best opposing order from the opposite heap until prices can no longer match or the new order is fully filled.

### Cancellation Logic
- **Active vs. Filled:** The engine keeps a dictionary of active orders (`active_orders`) and a set of filled orders (`filled_orders`).
- **Check `filled_orders`:** If an order is already fully filled, the cancel attempt fails: `"Failed - already fully filled"`.
- **Check `active_orders`:** If an order isn’t present in active_orders, it’s not eligible for cancellation: `"Failed – no such active order"`.
- **Otherwise:** Remove it from `active_orders` and return `"OK"`.

## Installation & Testing

### 1. Clone the Repository
```
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Python Environment
- Python 3.8+ recommended.
- Install requirements
    ```
    pip install -r requirements.txt
    ```

### 3. Run or Import
- Use the `OrderBook` class directly in your Python scripts.
- If you have a separate test suite (e.g., pytest or unittest), run:
    ```
    pytest
    ```
    or:
    ```
    python -m unittest
    ```