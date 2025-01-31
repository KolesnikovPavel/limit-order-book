"""
Main module with limit order book implementation.
"""

import heapq
from itertools import count

# global order number generator
order_number_generator = count(start=1)


class Order:
    """
    Base order class. Represents a single order in order book
    """
    __slots__ = ('order_id', 'side', 'price', 'quantity', 'order_number')

    def __init__(self, order_id: str, side: str, price: float, quantity: int):
        # validate order side
        if side.lower() not in {'buy', 'sell'}:
            raise ValueError(f'Invalid side: {side}. Must be "buy" or "sell"')

        # ensure price and quantity are positive
        if price <= 0 or quantity <= 0:
            raise ValueError('Price and quantity must be positive values')

        self.order_id = order_id
        self.side = side.lower()  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity

        # automatically assign order number for FIFO processing
        self.order_number = next(order_number_generator)

    def __lt__(self, other):
        """
        Defines ordering for heapq to prioritize:
        - Buy orders: Higher price first, then earlier order number
        - Sell orders: Lower price first, then earlier order number
        """
        if self.side == 'buy':
            # higher price first in a buy-heap
            return (self.price, -self.order_number) > (other.price, -other.order_number)
        # lower price first in a sell-heap
        return (self.price, self.order_number) < (other.price, other.order_number)


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
        # prevent placing an order with missing parameters
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

        # create a new order instance
        order = Order(order_id, side, price, quantity)

        # determine order placement based on its side
        if order.side == 'buy':
            current_heap = self.heap_buy_orders
            opposite_heap = self.heap_sell_orders
            condition = lambda buy_price, sell_price: buy_price >= sell_price
        else:  # sell
            current_heap = self.heap_sell_orders
            opposite_heap = self.heap_buy_orders
            condition = lambda sell_price, buy_price: sell_price <= buy_price

        # try to match the order against opposite orders
        match_items = self._process_order(
            order,
            current_heap,
            opposite_heap,
            condition
        )

        # if no match items, simply confirm order placement
        if not match_items:
            return 'OK'

        # determine if the order was partially or fully matched
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

        # move order to canceled orders and remove from active orders
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
            # get the best opposite order (lowest sell price or highest buy price)
            opposite_order = opposite_orders[0]

            # ensure the opposite order is still active
            if opposite_order.order_id not in self.active_orders:
                heapq.heappop(opposite_orders)
                continue

            # check if the order can be matched
            if not condition(order.price, opposite_order.price):
                break

            # remove the matched order from the heap
            heapq.heappop(opposite_orders)

            # calculate the quantity that can be matched
            matched_quantity = min(order.quantity, opposite_order.quantity)
            matched_orders.append(
                f'{opposite_order.order_id} '
                f'({matched_quantity} @ {opposite_order.price})'
            )

            # adjust quantities after matching
            order.quantity -= matched_quantity
            opposite_order.quantity -= matched_quantity

            # if partially filled, add back into the heap
            # else more order to filled orders and remove from active orders
            if opposite_order.quantity:
                heapq.heappush(opposite_orders, opposite_order)
            else:
                self.filled_orders[opposite_order.order_id] = opposite_order
                del self.active_orders[opposite_order.order_id]

        # if not fully matched, add to active orders and push it into the heap,
        # else add it to filled orders
        if order.quantity:
            self.active_orders[order.order_id] = order
            heapq.heappush(current_heap, order)
        else:
            self.filled_orders[order.order_id] = order

        return matched_orders
