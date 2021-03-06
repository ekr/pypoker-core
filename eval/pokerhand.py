import array
from deck.deck import Card
import hand
from handvalue import HandValue

# PP_straights contains a bit string representation of every possible straight, in value order
# each bit represents a card, with 1 = 2, 10 = 3, etc, up to 1<<12 = Ace.  Lowest straight 
# is the wheel, which is A2345
PP_straights = [ 0b1000000001111, 0b11111, 0b111110, 0b1111100, 0b11111000, 0b111110000, 0b1111100000,\
                 0b11111000000, 0b111110000000, 0b1111100000000 ]

def fix(x):
    """ fix a card value when counting backwards """
    return Card.CV_ACE - x

def get_top_cards(x, need_bits):
    """ given an integer bit vector, return the vector containing only the top need_bits cards """
    cur_val = 1 << Card.CV_ACE
    result = 0

    while need_bits and cur_val:
        if x & cur_val:
            result |= cur_val
            need_bits -= 1
        cur_val = cur_val >> 1

    return result


class PokerHand(hand.Hand):

    def find_kicker(self, exclude_card):
        """ find the highest card in the hand that isn't the given card.  (given card is in reverse value) """
        for card,val_count in enumerate(reversed(self.values)):
            if ((val_count > 0) and (card != exclude_card)):
                return fix(card)

        return -1

    def is_str_flush(self):
        """ return the handvalue object if the hand contains a straight flush, False otherwise """

        for cur_suit, x in enumerate(reversed(self.suits)):
            if (x > 4):
                for lo_card,straight_mask in enumerate(reversed(PP_straights)):
                    if (self.vals_in_suit[3 - cur_suit] & straight_mask) == straight_mask:
                        return HandValue(HandValue.HV_STR_FLUSH, fix(lo_card), 3-cur_suit, 0)
        return False

    def is_quads(self):
        """ return the handvalue object if the hand contains four of a kind, False otherwise """
        
        for cur_val, val_count in enumerate(reversed(self.values)):
            if (val_count > 3):
                return HandValue(HandValue.HV_QUADS, fix(cur_val), 0, self.all_values)

        return False

    def is_full_house(self):
        """ return the handvalue object for a full house, False otherwise """

        # look for the highest set of three
        for trip_val, trip_count in enumerate(reversed(self.values)):
            if (trip_count == 3):
                # look for the highest pair or better that isn't the highest trip
                # note that we can have two or more trips which translates to a FH
                for pair_val, pair_count in enumerate(reversed(self.values)):
                    if ((pair_count > 1) and (pair_val != trip_val)):
                        return HandValue(HandValue.HV_FULL_HOUSE, fix(trip_val), fix(pair_val), 0)
        
        return False

    def is_flush(self):
        """ return the handvalue for a flush, False otherwise """

        for suit, suit_count in enumerate(reversed(self.suits)):
            if (suit_count > 4):
                # found a flush.  we'll use the value vector to disambiguate
                real_suit = 3 - suit

                #vals_in_suit contains a bit vector with each value of that suit
                #in the hand.  We need to take the top 5 bits of that value, and
                #zero the rest.
                result = get_top_cards(self.vals_in_suit[real_suit], 5)
        
                top_card = Card.CV_ACE
                while ((result & (1 << top_card)) == 0) and (top_card > 0):
                    top_card -= 1

                #construct and return the handvalue
                return HandValue(HandValue.HV_FLUSH, top_card, result, real_suit)
        
        return False

    def is_straight(self):
        """ return the handvalue if this hand contains a straight, False otherwise """

        # self.all_values is a bitvector of all values present, regardless of suit
        # we can now just check that vector for the highest straight pattern

        for lo_card,straight_mask in enumerate(reversed(PP_straights)):
            if (self.all_values & straight_mask) == straight_mask:
                return HandValue(HandValue.HV_STRAIGHT, fix(lo_card), 0, 0)

        return False

    def is_trips(self):
        """ return the handvalue if this hand contains three of a kind, False otherwise """

        for card, card_count in enumerate(reversed(self.values)):
            if (card_count > 2):
                # found the set of three.  we make the secondary the value bit vector
                # this will make sure that hands with the same set of three but different
                # kickers and second kickers compare correctly
                return HandValue(HandValue.HV_TRIPS, fix(card), 0, self.all_values)
        
        return False
                
    def has_pairs(self):
        """ return the handvalue if the hand contains one or two pair, False otherwise """
        
        pairs_found = 0
        last_pair = 0

        for card, card_count in enumerate(reversed(self.values)):
            if (card_count > 1):
                pairs_found += 1
                if (pairs_found == 2):
                    return HandValue(HandValue.HV_TWO_PAIR, fix(last_pair), fix(card), self.all_values)
                else:
                    last_pair = card
        
        if pairs_found:
            return HandValue(HandValue.HV_PAIR, fix(last_pair), 0, self.all_values)
        
        return False

    eval_order = [ is_str_flush, is_quads, is_full_house, is_flush, \
                       is_straight, is_trips, has_pairs ]

    def get_hand_value(self):
        """ get the handvalue object that describes the conventional poker ranking of this hand """

        for func in self.eval_order:
            out = func(self)
            if out != False:
                return out

        # hand doesn't have any value other than high card
        return HandValue(HandValue.HV_HIGH_CARD, 0, 0, self.all_values)
