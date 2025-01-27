"""
Main module with limit order book implementation
"""

class Order:
    """
    Base order class
    """
    __slots__ = ('order_id', 'side', 'price', 'quantity')

    def __init__(self, order_id: str, side: str, price: float, quantity: int):
        self.order_id = order_id
        self.side = side  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity


class OrderBook:
    """
    Base order book class
    """
    __slots__ = ('active_orders', 'filled_orders')

    def __init__(self):
        self.active_orders = {}  # {'AAA': Order, 'BBB': Order, ...}

        self.filled_orders = set()  # {'AAA', 'BBB', ...}

    def place_order(
        self, order_id: str, side: str, price: float, quantity: int
    ) -> str:
        side = side.lower()
        order = Order(order_id, side, price, quantity)

        full_match, match_items = self._process_order(order)
        if not full_match:
            self.active_orders[order_id] = order

        if not match_items:
            return 'OK'

        match_type = 'Fully' if full_match else 'Partially'
        match_items_str = ' and '.join(match_items)
        return f'{match_type} matched with {match_items_str}'

    def cancel_order(self, order_id: str):
        """
        Cancel an order if it is still active
        """
        if order_id in self.filled_orders:
            return 'Failed - already fully filled'

        if order_id not in self.active_orders:
            return 'Failed – no such active order'

        del self.active_orders[order_id]
        return 'OK'

    # TODO: simplify and optimize
    def _process_order(self, new_order):
        new_price = new_order.price
        if new_order.side == 'buy':
            search_order_side = 'sell'
            condition = lambda price_1, price_2: price_1 >= price_2
        elif new_order.side == 'sell':
            search_order_side = 'buy'
            condition = lambda price_1, price_2: price_2 >= price_1
        else:
            raise ValueError('ValueError – no such side')

        matched_orders = []
        full_match = False

        # TODO: replace loop with something more efficient
        for order_id, order in self.active_orders.items():
            if order.side != search_order_side:
                continue

            if not condition(new_price, order.price):
                continue

            matched_quantity = min(new_order.quantity, order.quantity)
            matched_orders.append(f'{order.order_id} ({matched_quantity} @ {order.price})')

            new_order.quantity -= matched_quantity
            order.quantity -= matched_quantity

            if new_order.quantity <= order.quantity:
                full_match = True
            else:
                self.filled_orders.add(order.order_id)

        for order_id in self.filled_orders:
            if order_id in self.active_orders:
                del self.active_orders[order_id]

        return full_match, matched_orders


book1 = OrderBook()
print(book1.place_order('AAA', 'Buy', 10, 10))  # ok
print(book1.place_order('BBB', 'Buy', 12, 12))  # ok
print(book1.place_order('CCC', 'Buy', 14, 14))  # ok
print(book1.cancel_order('CCC'))  # ok
print(book1.place_order('DDD', 'Sell', 15, 10))  # ok
print(book1.place_order('EEE', 'Sell', 12, 2))  # Fully matched with BBB (2 @ 12)
print(book1.place_order('FFF', 'Sell', 12, 4))  # Fully matched with BBB (4 @ 12)
print(book1.place_order('GGG', 'Sell', 12, 10))  # Partially matched with BBB (6 @ 12)
print(book1.cancel_order('BBB'))  # Failed - already fully filled
print(book1.place_order('HHH', 'Buy', 12, 14))  # Partially matched with GGG (4 @ 12)
print(book1.place_order('KKK', 'Sell', 10, 20))  # Fully matched with HHH (10 @ 12) and AAA (10 @ 10)
print(book1.cancel_order('DDD'))  # ok
print(book1.cancel_order('DDD'))  # Failed – no such active order