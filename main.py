"""
Main module with limit order book implementation
"""

import heapq


class Order:
    """
    Base order class
    """
    __slots__ = ('order_id', 'side', 'price', 'quantity')

    def __init__(self, order_id: str, side: str, price: float, quantity: int):
        self.order_id = order_id
        self.side = side.lower()  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f'{self.order_id} {self.side} {self.price} {self.quantity}'

    def __repr__(self):
        return f'{self.order_id}_{self.side}_{self.price}_{self.quantity}'

    def __lt__(self, other):
        """
        """
        if self.side == 'buy':
            # higher price first in a buy-heap
            return self.price > other.price
        # lower price first in a sell-heap
        return self.price < other.price

class OrderBook:
    """
    Base order book class
    """
    __slots__ = (
        'active_orders','heap_buy_orders', 'heap_sell_orders', 'filled_orders'
    )

    def __init__(self):
        self.active_orders = {}  # {'AAA': Order, 'BBB': Order ...}

        self.filled_orders = set()  # {'AAA', 'BBB', ...}

        self.heap_buy_orders = []  # max-heap of buy orders
        self.heap_sell_orders = []  # min-heap of sell orders

    def place_order(
        self, order_id: str, side: str, price: float, quantity: int
    ) -> str:
        """
        Place an order

        :param order_id:
        :param side:
        :param price:
        :param quantity:
        :return:
        """
        if not all([order_id, side, price, quantity]):
            raise ValueError(
                'Invalid parameters: order_id, side, price and quantity '
                'are required'
            )

        order = Order(order_id, side, price, quantity)

        if order.side == 'buy':
            current_heap = self.heap_buy_orders
            match_items = self._process_order(
                order=order,  # buy order
                opposite_orders=self.heap_sell_orders,
                condition=lambda buy_price, sell_price: buy_price >= sell_price
            )
        elif order.side == 'sell':
            current_heap = self.heap_sell_orders
            match_items = self._process_order(
                order=order,  # sell order
                opposite_orders=self.heap_buy_orders,
                condition=lambda sell_price, buy_price: sell_price <= buy_price
            )
        else:
            raise ValueError(f'ValueError – no such side: {side}')

        if order.quantity:
            self.active_orders[order.order_id] = order
            heapq.heappush(current_heap, order)

        if not match_items:
            return 'OK'

        match_type = 'Partially' if order.quantity else 'Fully'
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

    def _process_order(self, order, opposite_orders, condition):
        """

        :param order:
        :param opposite_orders:
        :param condition:
        :return:
        """
        matched_orders = []

        while opposite_orders and order.quantity:
            # get the best order of the opposite side
            opposite_order = heapq.heappop(opposite_orders)

            if opposite_order.order_id not in self.active_orders:
                continue

            # opposite order price ...
            if not condition(order.price, opposite_order.price):
                heapq.heappush(opposite_orders, opposite_order)
                break

            matched_quantity = min(order.quantity, opposite_order.quantity)
            matched_orders.append(f'{opposite_order.order_id} ({matched_quantity} @ {opposite_order.price})')

            order.quantity -= matched_quantity
            opposite_order.quantity -= matched_quantity

            if opposite_order.quantity:
                heapq.heappush(opposite_orders, opposite_order)
            else:
                self.filled_orders.add(opposite_order.order_id)

        return matched_orders


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
