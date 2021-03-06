from deck.deck import Deck, Card
from eval.hand import Hand
from eval.handvalue import HandValue
from eval.pokerhand import PokerHand
import unittest

class TestDeckFunctions(unittest.TestCase):
    def test_card(self):
        x = Card('Ah')

        #case 1: make sure that when we set a card, the value is consistent
        self.assertTrue(x.short_name() == 'Ah')
        self.assertTrue(x.single_name() == 'Y')

        #case 2: make sure that when we set a card, the suit and value match
        y = Card('Ad')
        self.assertTrue(x.value == y.value)

        #case 3: make sure that Ah and Ad have different suits
        self.assertFalse(x.suit == y.suit)
        
        #case 4: test setting the card by long name
        y.set_value_by_name('Deuce')
        y.set_suit_by_name('Hearts')
        self.assertTrue(y.short_name() == '2h')

    def test_deck(self):
        x = Deck()
        x.shuffle()

        #case 1:  make sure a shuffled deck has all the cards
        self.assertTrue(len(x) == 52)
        self.assertTrue(len(x.deck_state()) == 52)

        #case 2:  pull a single card and make sure the deck shrinks
        c = x.deal_one()
        self.assertTrue(len(x) == 51)
        self.assertTrue(len(x.deck_state()) == 51)

        #case 3:  reshuffle and make sure the deck is whole
        x.reset()
        self.assertTrue(len(x) == 52)
        self.assertTrue(len(x.deck_state()) == 52)

        #case 4:  reshuffle, take a specific card, and insure the deck shrinks
        x.reset()
        c = Card('Ah')
        x.take_card(c)
        self.assertTrue(len(x) == 51)

        #case 5:  make sure we can't take the same card twice
        self.assertTrue(x.take_card(c) == -1)

        #case 6:  get a five card hand
        x.reset()
        l = x.deal_hand(5)
        self.assertTrue(len(l) == 5)
        self.assertTrue(len(x) == 52-5)

        #case 7:  shuffle, make sure the length is unchanged
        x.shuffle()
        self.assertTrue(len(x) == 52-5)

    def test_restore(self):
        x = Deck()
        x.shuffle()
        
        y = x.deck_state()
        z = Deck()
        self.assertTrue(z.restore_deck(y) == True)
        self.assertTrue(z.deck_state() == x.deck_state())
        z.shuffle()
        self.assertFalse(z.deck_state() == x.deck_state())

class TestHandFunctions(unittest.TestCase):
    def test_hand(self):
        x = Hand()
        base_deck = Deck()

        #case 1:  add some cards, make sure the hand goes to the right length
        x.add_cards([2, 3, 4, 5], base_deck)
        self.assertTrue(len(x) == 4)

        #case 2:  add some illegal cards, make sure they are not added
        x.add_cards([-1, 55, 'q'], base_deck)
        self.assertTrue(len(x) == 4)

        #case 4: add an initialized card object
        base_deck.reset()
        c1 = Card('As')
        x.add_cards([c1], base_deck)
        self.assertTrue(len(x) == 5)

        #case 5: test adding cards with string names
        base_deck.reset()
        y = Hand()
        y.add_cards(['Ah', 'As', '5d'], base_deck)
        self.assertTrue(len(y) == 3)

        #case 6: insure duplicate strings don't add
        y.add_cards(['Ah'], base_deck)
        self.assertTrue(len(y) == 3)

        #case 7: add from a string
        base_deck.reset()
        y = Hand()
        y.add_cards('AhAdAs2d', base_deck)
        self.assertTrue(len(y) == 4)

        #case 8: make sure we can't pull a card twice from a deck
        z = Hand()
        z.add_cards('AhAdAs2d5d', base_deck)
        self.assertTrue(len(z) == 1)

class TestPokerHandFunctions(unittest.TestCase):
    def test_str_flush(self):
        x = PokerHand()

        #case 1:  make sure the empty hand is not a straight flush
        self.assertFalse(x.is_str_flush())

        #case 2:  make sure four to a straight flush is not a straight flush
        x.add_cards('AhKhQhJh', None)
        self.assertFalse(x.is_str_flush())

        #case 3: make sure we find the ace high straight flush
        x.add_cards(['Th'], None)
        out = x.is_str_flush()
        self.assertTrue(out.type == HandValue.HV_STR_FLUSH)
        self.assertTrue(out.primary == Card.CV_ACE)
        self.assertTrue(out.secondary == Card.SV_HEARTS)

        #case 4: extend the str flush on the low end, make sure it doens't change
        x.add_cards(['9h'], None)
        self.assertTrue(x.is_str_flush().primary == Card.CV_ACE)

        y = PokerHand()

        #case 5: check that the wheel works
        y.add_cards('Ad2d3d4d5d', None)
        self.assertTrue(y.is_str_flush().primary == Card.CV_FIVE)

        #case 6: add the 6, make sure it changes
        y.add_cards(['6d'], None)
        self.assertTrue(y.is_str_flush().primary == Card.CV_SIX)

        #case 7: make sure that a flush is not a straight flush
        z = PokerHand()
        z.add_cards('AcJcTc9c8c', None)
        self.assertFalse(z.is_str_flush())

        #case 8: make it a straight and flush, but not str_flush
        z.add_cards(['7d'], None)
        self.assertFalse(z.is_str_flush())

    def test_quads(self):
        a = PokerHand()
        
        #case 1: make sure the empty hand isn't quads
        self.assertFalse(a.is_quads())

        #case 2: make sure trips aren't quads
        a.add_cards('5d5s5h', None)
        self.assertFalse(a.is_quads())

        #case 3: quads with no kicker
        a.add_cards(['5c'], None)
        self.assertTrue(a.is_quads().primary == Card.CV_FIVE)
        self.assertTrue(a.is_quads().type == HandValue.HV_QUADS)
        self.assertTrue(a.is_quads().secondary == 0)

        #case 4: add a kicker
        a.add_cards(['As'], None)
        self.assertTrue(a.is_quads().primary == Card.CV_FIVE)
        self.assertTrue(a.is_quads().type == HandValue.HV_QUADS)

    def test_full_house(self):
        a = PokerHand()

        #case 1: make sure the empty hand isn't a full house
        self.assertFalse(a.is_full_house())

        #case 2: check an example full house
        a.add_cards('AdAhKsKdKh', None)
        self.assertTrue(a.is_full_house().primary == Card.CV_KING)
        self.assertTrue(a.is_full_house().type == HandValue.HV_FULL_HOUSE)
        self.assertTrue(a.is_full_house().secondary == Card.CV_ACE)

        #case 3: add a card which should reverse the primary and secondary
        a.add_cards(['As'], None)
        self.assertTrue(a.is_full_house().primary == Card.CV_ACE)
        self.assertTrue(a.is_full_house().type == HandValue.HV_FULL_HOUSE)
        self.assertTrue(a.is_full_house().secondary == Card.CV_KING)

        #case 4: make sure that two pair doesn't show up as a FH
        a = PokerHand()
        a.add_cards('5h5s4h4dAd', None)
        self.assertFalse(a.is_full_house())

    def test_flush(self):
        a = PokerHand()

        #case 1:  make sure that the empty hand isn't a flush
        self.assertFalse(a.is_flush())

        #case 2:  test that we sense a flush
        a.add_cards('AsTs6s5s3s', None)
        self.assertTrue(a.is_flush().type == HandValue.HV_FLUSH)

        #case 3: a six card and five card flush should be equal if the top five cards are the same
        b = PokerHand()
        b.add_cards(['As', 'Ts', '6s', '5s', '3s', '2s'], None)
        out = b.is_flush()
        self.assertTrue(out.type == HandValue.HV_FLUSH)
        self.assertTrue(out.primary == a.is_flush().primary)

        #case 4: now change one flush so it's a higher set of cards
        b.add_cards('Ks', None)
        out = b.is_flush()
        self.assertTrue(out.type == HandValue.HV_FLUSH)
        self.assertTrue(out.secondary > a.is_flush().secondary)

    def test_straight(self):
        a = PokerHand()
        
        #case 1: make sure the empty hand isn't a flush
        self.assertFalse(a.is_straight())

        #case 2: make sure we sense a straight
        a.add_cards('9s8c7d6h5h', None)
        out = a.is_straight()
        self.assertTrue(out.type == HandValue.HV_STRAIGHT)
        self.assertTrue(out.primary == Card.CV_NINE)

        #case 3: make sure adding a lower card doesn't alter the straight
        a.add_cards(['4h'], None)
        out = a.is_straight()
        self.assertTrue(out.type == HandValue.HV_STRAIGHT)
        self.assertTrue(out.primary == Card.CV_NINE)

        #case 4: add a higher card, make sure the straight improves
        a.add_cards(['Td'], None)
        out = a.is_straight()
        self.assertTrue(out.type == HandValue.HV_STRAIGHT)
        self.assertTrue(out.primary == Card.CV_TEN)
    
    def test_trips(self):
        a = PokerHand()

        #case 1: make sure the empty hand doesn't contain trips
        self.assertFalse(a.is_trips())

        #case 2: make sure we sense trips in three cards
        a.add_cards('9s9h9c', None)
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())
        out = a.is_trips()
        self.assertTrue(out.type == HandValue.HV_TRIPS)
        self.assertTrue(out.primary == Card.CV_NINE)

        #case 3: add a kicker
        a.add_cards(['Ah'], None)
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())
        out = a.is_trips()
        self.assertTrue(out.type == HandValue.HV_TRIPS)
        self.assertTrue(out.primary == Card.CV_NINE)

        #case 4: make the same trips, but with worse kicker
        b = PokerHand()
        b.add_cards('9s9h9cKd', None)
        out2 = b.is_trips()
        self.assertTrue(out2.type == HandValue.HV_TRIPS)
        self.assertTrue(out2.primary == Card.CV_NINE)
        self.assertTrue(out.tertiary > out2.tertiary)

        #case 5: check subkicker...make and b have the same kicker, but smaller subkick
        a.add_cards(['Qd'], None)
        b.add_cards(['Ah'], None)
        out = a.is_trips()
        out2 = b.is_trips()
        self.assertTrue(out2.type == HandValue.HV_TRIPS)
        self.assertTrue(out2.primary == Card.CV_NINE)
        self.assertTrue(out2.tertiary > out.tertiary)

    def test_pairs(self):
        a = PokerHand()

        #case 1: make sure the empty hand doesn't contain two pair
        self.assertFalse(a.has_pairs())

        #case 2: sense two pair in four cards
        a.add_cards(['Ad', 'As', '4h', '4c'], None)
        self.assertFalse(a.is_trips())
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())
        out = a.has_pairs()
        self.assertTrue(out.type == HandValue.HV_TWO_PAIR)
        self.assertTrue(out.primary == Card.CV_ACE)
        self.assertTrue(out.secondary == Card.CV_FOUR)

        #case 3: add a kicker
        a.add_cards(['3d'], None)
        self.assertFalse(a.is_trips())
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())        
        out = a.has_pairs()
        self.assertTrue(out.type == HandValue.HV_TWO_PAIR)
        self.assertTrue(out.primary == Card.CV_ACE)
        self.assertTrue(out.secondary == Card.CV_FOUR)
        
        #case 4: add a better kicker, make sure comparison works
        a.add_cards(['Kd'], None)
        self.assertFalse(a.is_trips())
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())        
        out2 = a.has_pairs()
        self.assertTrue(out2.type == HandValue.HV_TWO_PAIR)
        self.assertTrue(out2.primary == Card.CV_ACE)
        self.assertTrue(out2.secondary == Card.CV_FOUR)
        self.assertTrue(out2.tertiary > out.tertiary)

        a = PokerHand()

        #case 5: sense a pair in two cards
        a.add_cards(['6d', '6s'], None)
        self.assertFalse(a.is_trips())
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())        
        out2 = a.has_pairs()
        self.assertTrue(out2.type == HandValue.HV_PAIR)
        self.assertTrue(out2.primary == Card.CV_SIX)

        #case 6: add cards, make sure outcome is the same
        a.add_cards(['8d'], None)
        self.assertFalse(a.is_trips())
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())        
        out = a.has_pairs()
        self.assertTrue(out.type == HandValue.HV_PAIR)
        self.assertTrue(out.primary == Card.CV_SIX)

        #case 7: improve the kicker, make sure hand improves
        a.add_cards(['9d'], None)
        self.assertFalse(a.is_trips())
        self.assertFalse(a.is_quads())
        self.assertFalse(a.is_straight())
        self.assertFalse(a.is_flush())        
        out2 = a.has_pairs()
        self.assertTrue(out2.type == HandValue.HV_PAIR)
        self.assertTrue(out2.primary == Card.CV_SIX)
        self.assertTrue(out2.tertiary > out.tertiary)

    def test_get_value(self):
        a = PokerHand()

        #case 1: check the empty hand
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_HIGH_CARD)
        self.assertTrue(out.primary == 0)

        #case 2: check a straight flush
        a = PokerHand()
        a.add_cards('AhKhQhJhTh', None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_STR_FLUSH)
        self.assertTrue(out.primary == Card.CV_ACE)

        #case 3: check a four of a kind
        a = PokerHand()
        a.add_cards(['Ah', 'Ad', 'As', 'Ac', 'Th', '6d'], None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_QUADS)
        self.assertTrue(out.primary == Card.CV_ACE)

        #case 4: check a full house
        a = PokerHand()
        a.add_cards(['Ah', 'Ad', 'Ks', 'Kc', 'Kh', '6d'], None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_FULL_HOUSE)
        self.assertTrue(out.primary == Card.CV_KING)
        self.assertTrue(out.secondary == Card.CV_ACE)

        #case 5: check a flush
        a = PokerHand()
        a.add_cards(['Ah', 'Ad', 'Kh', 'Jh', '5h', '6h'], None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_FLUSH)

        #case 6: check a straight
        a = PokerHand()
        a.add_cards(['Ah', '2d', '3s', '4d', '5h', 'Kh'], None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_STRAIGHT)

        #case 7: check a three of a kind
        a = PokerHand()
        a.add_cards(['Ah', '2d', '3s', '5d', '5h', '5s'], None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_TRIPS)
        self.assertTrue(out.primary == Card.CV_FIVE)

        #case 8: check two pair
        a = PokerHand()
        a.add_cards(['Ah', 'Ad', '3s', '3d', '4h', '5s'], None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_TWO_PAIR)
        self.assertTrue(out.primary == Card.CV_ACE)
        self.assertTrue(out.secondary == Card.CV_THREE)

        #case 9: check a pair
        a = PokerHand()
        a.add_cards('AhAd2sJd4h5s', None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_PAIR)
        self.assertTrue(out.primary == Card.CV_ACE)

        #case 10: check a high card hand
        a = PokerHand()
        a.add_cards('AhQd2sJd4h5s', None)
        out = a.get_hand_value()
        self.assertTrue(out.type == HandValue.HV_HIGH_CARD)

if __name__ == '__main__':
    unittest.main()
