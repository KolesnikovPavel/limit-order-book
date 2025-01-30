"""
Unit tests for limit order book implementation.
"""

import pytest

from main import OrderBook


@pytest.fixture
def test_order_book():
    """
    Provides a new instance of the OrderBook for each test
    """
    return OrderBook()


def test_base_case(test_order_book):
    """
    Basic test case covering order placement, matching, and cancellations
    """
    assert test_order_book.place_order('AAA', 'Buy', 10, 10) == 'OK'
    assert test_order_book.place_order('BBB', 'Buy', 12, 12) == 'OK'
    assert test_order_book.place_order('CCC', 'Buy', 14, 14) == 'OK'
    assert test_order_book.cancel_order('CCC') == 'OK'
    assert test_order_book.place_order('DDD', 'Sell', 15, 10) == 'OK'
    assert test_order_book.place_order('EEE', 'Sell', 12, 2) == 'Fully matched with BBB (2 @ 12)'
    assert test_order_book.place_order('FFF', 'Sell', 12, 4) == 'Fully matched with BBB (4 @ 12)'
    assert test_order_book.place_order('GGG', 'Sell', 12, 10) == 'Partially matched with BBB (6 @ 12)'
    assert test_order_book.cancel_order('BBB') == 'Failed - already fully filled'
    assert test_order_book.place_order('HHH', 'Buy', 12, 14) == 'Partially matched with GGG (4 @ 12)'
    assert test_order_book.place_order('KKK', 'Sell', 10, 20) == 'Fully matched with HHH (10 @ 12) and AAA (10 @ 10)'
    assert test_order_book.cancel_order('DDD') == 'OK'
    assert test_order_book.cancel_order('DDD') == 'Failed – no such active order'


def test_large_order_split(test_order_book):
    """
    Tests that a large order is correctly matched with multiple smaller orders
    """
    assert test_order_book.place_order('B1', 'Buy', 100, 10) == 'OK'
    assert test_order_book.place_order('S1', 'Sell', 100, 3) == 'Fully matched with B1 (3 @ 100)'
    assert test_order_book.place_order('S2', 'Sell', 100, 4) == 'Fully matched with B1 (4 @ 100)'
    assert test_order_book.place_order('S3', 'Sell', 100, 3) == 'Fully matched with B1 (3 @ 100)'


def test_price_priority(test_order_book):
    """
    Ensures that higher bid orders get priority in matching
    """
    assert test_order_book.place_order('B1', 'Buy', 100, 5) == 'OK'
    assert test_order_book.place_order('B2', 'Buy', 110, 5) == 'OK'
    assert test_order_book.place_order('S1', 'Sell', 105, 5) == 'Fully matched with B2 (5 @ 110)'


def test_sell_order_priority(test_order_book):
    """
    Ensures that lower priced sell orders get priority in matching
    """
    assert test_order_book.place_order('S1', 'Sell', 105, 5) == 'OK'
    assert test_order_book.place_order('S2', 'Sell', 100, 5) == 'OK'
    assert test_order_book.place_order('B1', 'Buy', 110, 10) == 'Fully matched with S2 (5 @ 100) and S1 (5 @ 105)'


def test_cancel_non_existent_order(test_order_book):
    """
    Ensures that canceling a non-existent order returns a failed result
    """
    assert test_order_book.cancel_order('NOPE') == 'Failed – no such active order'


def test_order_lifecycle(test_order_book):
    """
    Tests the full lifecycle of an order: placement, execution, and cancellation
    """
    assert test_order_book.place_order('O1', 'Buy', 50, 10) == 'OK'
    assert test_order_book.cancel_order('O1') == 'OK'
    assert test_order_book.cancel_order('O1') == 'Failed – no such active order'


def test_cancel_filled_order(test_order_book):
    """
    Checks that canceling an already filled order is not allowed
    """
    assert test_order_book.place_order('B1', 'Buy', 100, 5) == 'OK'
    assert test_order_book.place_order('S1', 'Sell', 90, 5) == 'Fully matched with B1 (5 @ 100)'
    assert test_order_book.cancel_order('B1') == 'Failed - already fully filled'


def test_multiple_orders_same_price(test_order_book):
    """
    Ensures that multiple orders at the same price are executed in FIFO order
    """
    assert test_order_book.place_order('B1', 'Buy', 100, 5) == 'OK'
    assert test_order_book.place_order('B2', 'Buy', 100, 5) == 'OK'
    assert test_order_book.place_order('S1', 'Sell', 100, 8) == 'Fully matched with B1 (5 @ 100) and B2 (3 @ 100)'


def test_invalid_orders(test_order_book):
    """
    Tests handling of invalid orders such as zero or negative values
    """
    with pytest.raises(ValueError, match='Price and quantity must be positive values'):
        test_order_book.place_order('B1', 'Buy', 10, -5)

    with pytest.raises(ValueError, match='Price and quantity must be positive values'):
        test_order_book.place_order('S1', 'Sell', -10, 5)

    with pytest.raises(ValueError, match='Order with this ID has already been placed'):
        test_order_book.place_order('B1', 'Buy', 50, 5)
        test_order_book.place_order('B1', 'Sell', 50, 5)


def test_extreme_price_variations(test_order_book):
    """
    Tests handling of orders with extreme price variations
    """
    assert test_order_book.place_order('X1', 'Buy', 0.01, 10) == 'OK'
    assert test_order_book.place_order('X2', 'Sell', 1000000, 1) == 'OK'
    assert test_order_book.place_order('X3', 'Sell', 0.01, 5) == 'Fully matched with X1 (5 @ 0.01)'
