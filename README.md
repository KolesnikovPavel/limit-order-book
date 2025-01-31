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
   - Among orders at the same price, the earliest one placed is matched first (FIFO priority is handled via an internal order number).

## Data Structures and Logic

The main components of the engine:

1. **`Order` Class**  
Holds basic attributes: `order_id`, `side`, `price`, `quantity` and an internally assigned `order_number` to ensure FIFO processing.  
It also defines a custom `__lt__` method to ensure correct priority in a heap:

   - For buy orders, higher prices should come out first (max-heap), then earlier order number.
   - For sell orders, lower prices should come out first (min-heap), then earlier order number.

2. **`OrderBook` Class**  
Manages active, filled, and canceled orders. It uses two heaps to store buy and sell orders for efficient matching.  
**Attributes:**
   - `active_orders`: A dictionary mapping order_id → Order for all currently active orders.
   - `filled_orders`: A dictionary tracking orders that have been fully matched.
   - `canceled_orders`: A dictionary storing canceled orders.
   - `heap_buy_orders`: A max-heap for buy orders.
   - `heap_sell_orders`: A min-heap for sell orders.

### Matching Mechanism
- **Heap Operations:**
Python's `heapq` (which implements a min-heap) is adapted to prioritize highest buy prices and lowest sell prices.
- **Processing an Order:**
When an order arrives, the _`process_order` method repeatedly attempts to match it with the best available opposite order.
- **Partial and Full Matching:**
Orders are processed until either:
  - The incoming order is fully filled.
  - No more matching orders are available.

### Order Placement (`place_order`)
- Ensures that an order ID is unique and validates input.
- Matches the order against the opposing queue.
- If unmatched, adds it to the active queue and corresponding heap.
- Returns a message indicating whether the order was fully matched, partially matched, or simply placed.

### Cancellation Logic (`cancel_order`)
- If an order is **fully filled**, cancellation fails (`"Failed - already fully filled"`).
- If an order is **not active**, cancellation fails (`"Failed - no such active order"`).
- Otherwise, the order is removed from active orders and stored in `canceled_orders`.

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