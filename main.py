"""
Main module with limit order book implementation.
"""

import heapq


class Order:
    """
    Base order class. Represents a single order in order book
    """
    __slots__ = ('order_id', 'side', 'price', 'quantity')

    def __init__(self, order_id: str, side: str, price: float, quantity: int):
        if side.lower() not in {'buy', 'sell'}:
            raise ValueError(f'Invalid side: {side}. Must be "buy" or "sell"')

        if price <= 0 or quantity <= 0:
            raise ValueError('Price and quantity must be positive values')

        self.order_id = order_id
        self.side = side.lower()  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity

    def __lt__(self, other):
        """
        Defines ordering for heapq to prioritize buy orders with higher prices
        and sell orders with lower prices
        """
        if self.side == 'buy':
            # higher price first in a buy-heap
            return self.price > other.price
        # lower price first in a sell-heap
        return self.price < other.price


class OrderBook:
    """
    Base order book class with buy and sell orders
    """
    __slots__ = (
        'active_orders',
        'filled_orders',
        'canceled_orders',
        'heap_buy_orders',
        'heap_sell_orders',
    )

    def __init__(self):
        self.active_orders = {}
        self.filled_orders = {}
        self.canceled_orders = {}

        self.heap_buy_orders = []  # max-heap of buy orders
        self.heap_sell_orders = []  # min-heap of sell orders

    def place_order(
        self, order_id: str, side: str, price: float, quantity: int
    ) -> str:
        """
        Place an order into the order book

        :param order_id: Unique order identifier
        :param side: Order side ('buy' or 'sell')
        :param price: Order price
        :param quantity: Order quantity
        :return:
        """
        if not all([order_id, side, price, quantity]):
            raise ValueError(
                'Invalid parameters: order_id, side, price and quantity '
                'are required'
            )

        # prevent placing an order if an order with the same ID
        # has already been encountered (active, filled, or canceled)
        if (
            order_id in self.active_orders
            or order_id in self.filled_orders
            or order_id in self.canceled_orders
        ):
            raise ValueError('Order with this ID has already been placed')

        order = Order(order_id, side, price, quantity)

        if order.side == 'buy':
            current_heap = self.heap_buy_orders
            opposite_heap = self.heap_sell_orders
            condition = lambda buy_price, sell_price: buy_price >= sell_price
        else:  # sell
            current_heap = self.heap_sell_orders
            opposite_heap = self.heap_buy_orders
            condition = lambda sell_price, buy_price: sell_price <= buy_price

        match_items = self._process_order(
            order,
            current_heap,
            opposite_heap,
            condition
        )

        if not match_items:
            return 'OK'

        match_type = 'Partially' if order.quantity else 'Fully'
        match_items_str = ' and '.join(match_items)

        return f'{match_type} matched with {match_items_str}'

    def cancel_order(self, order_id: str):
        """
        Cancel an order if it is still active

        :param order_id: Unique order identifier
        :return:
        """
        if order_id in self.filled_orders:
            return 'Failed - already fully filled'

        if order_id not in self.active_orders:
            return 'Failed – no such active order'

        order = self.active_orders[order_id]
        self.canceled_orders[order_id] = order

        del self.active_orders[order_id]
        return 'OK'

    def _process_order(self, order, current_heap, opposite_orders, condition):
        """
        Match an order against opposite side orders

        :param order: The order being placed
        :param current_heap: The heap of current-side orders
        :param opposite_orders: The heap of opposite-side orders
        :param condition: A function defining the matching condition
        :return:
        """
        matched_orders = []

        while opposite_orders and order.quantity:
            # get the best opposite order
            opposite_order = opposite_orders[0]

            # ensure the opposite order is still active
            if opposite_order.order_id not in self.active_orders:
                heapq.heappop(opposite_orders)
                continue

            # check if the order can be matched
            if not condition(order.price, opposite_order.price):
                break

            # remove after checking condition
            heapq.heappop(opposite_orders)

            matched_quantity = min(order.quantity, opposite_order.quantity)
            matched_orders.append(
                f'{opposite_order.order_id} '
                f'({matched_quantity} @ {opposite_order.price})'
            )

            order.quantity -= matched_quantity
            opposite_order.quantity -= matched_quantity

            # if partially filled, add back
            if opposite_order.quantity:
                heapq.heappush(opposite_orders, opposite_order)
            else:
                self.filled_orders[opposite_order.order_id] = opposite_order

        # if not fully matched, add to active orders and push it into the heap,
        # else add it to filled orders
        if order.quantity:
            self.active_orders[order.order_id] = order
            heapq.heappush(current_heap, order)
        else:
            self.filled_orders[order.order_id] = order

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
