"""

"""

from main import OrderBook


def test_base_case():
    test_book = OrderBook()

    assert test_book.place_order('AAA', 'Buy', 10, 10) == 'OK'
    assert test_book.place_order('BBB', 'Buy', 12, 12) == 'OK'
    assert test_book.place_order('CCC', 'Buy', 14, 14) == 'OK'
    assert test_book.cancel_order('CCC') == 'OK'
    assert test_book.place_order('DDD', 'Sell', 15, 10) == 'OK'
    assert test_book.place_order('EEE', 'Sell', 12, 2) == 'Fully matched with BBB (2 @ 12)'
    assert test_book.place_order('FFF', 'Sell', 12, 4) == 'Fully matched with BBB (4 @ 12)'
    assert test_book.place_order('GGG', 'Sell', 12, 10) == 'Partially matched with BBB (6 @ 12)'
    assert test_book.cancel_order('BBB') == 'Failed - already fully filled'
    assert test_book.place_order('HHH', 'Buy', 12, 14) == 'Partially matched with GGG (4 @ 12)'
    # FIXME
    # assert test_book.place_order('KKK', 'Sell', 10, 20) == 'Fully matched with HHH (10 @ 12) and AAA (10 @ 10)'
    assert test_book.cancel_order('DDD') == 'OK'
    assert test_book.cancel_order('DDD') == 'Failed – no such active order'
