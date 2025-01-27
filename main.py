"""
Main module with limit order book implementation
"""

class Order:
    def __init__(self, id, side, price, quantity):
        self.id = id
        self.side = side
        self.price = price
        self.quantity = quantity


class OrderBook:

    def __init__(self):
        self.orders = {}
        self.filled_orders = set()

    def place_order(self, id, side, price, quantity):
        side = side.lower()
        order = Order(id, side, price, quantity)

        full_match, match_items = self._calc_match(order)

        if not full_match:
            self.orders[id] = order

        if not match_items:
            return 'OK'

        match_type = 'Fully' if full_match else 'Partially'
        match_items_str = ' and '.join(match_items)
        return f'{match_type} matched with {match_items_str}'

    def cancel_order(self, id):
        if id in self.filled_orders:
            return 'Failed - already fully filled'

        if id not in self.orders:
            return 'Failed – no such active order'

        del self.orders[id]
        return 'OK'

    # TODO: simplify and optimize
    def _calc_match(self, new_order):
        new_price = new_order.price
        if new_order.side == 'buy':
            search_order_side = 'sell'
            condition = lambda price_1, price_2: price_1 >= price_2
        elif new_order.side == 'sell':
            search_order_side = 'buy'
            condition = lambda price_1, price_2: price_2 >= price_1
        else:
            raise ValueError('ValueError – no such side')

        matched_items = []
        full_match = False

        # TODO: replace loop with something more efficient
        for order_id, order in self.orders.items():
            if order.side != search_order_side:
                continue

            if not condition(new_price, order.price):
                continue

            if new_order.quantity > order.quantity:
                quantity = order.quantity
                new_order.quantity -= order.quantity
                self.filled_orders.add(order.id)
            elif new_order.quantity < order.quantity:
                quantity = new_order.quantity
                order.quantity -= new_order.quantity
                full_match = True
            else:
                quantity = order.quantity
                order.quantity -= new_order.quantity
                self.filled_orders.add(order.id)
                full_match = True

            matched_items.append(
                f'{order.id} ({quantity} @ {order.price})'
            )

        for order_id in self.filled_orders:
            if order_id in self.orders:
                del self.orders[order_id]

        return full_match, matched_items


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
print(book1.place_order('HHH', 'Buy', 12, 14))  # Fully matched with GGG (4 @ 12)
print(book1.place_order('KKK', 'Sell', 10, 20))  # Fully matched with HHH (10 @ 12) and AAA (10 @ 10)
print(book1.cancel_order('DDD'))  # ok
print(book1.cancel_order('DDD'))  # Failed – no such active order