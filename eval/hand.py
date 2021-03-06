import array
from deck.deck import Card

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.suits = array.array('i', [0]*4)
        self.values = array.array('i', [0]*13)
        self.vals_in_suit = array.array('i', [0]*4)
        self.all_values = 0

    def add_cards(self, new_cards, use_deck):
        """ add a set of cards to a hand, taking the cards from the given deck,  each card in 
        the set must be a card object, card name, or canonical index """

        to_add = new_cards

        #if we get a string, make it into a set of cards
        if (isinstance(new_cards, str)):
            to_add = []
            card_str = new_cards
            while len(card_str) > 1:
                to_add.append(card_str[:2])
                card_str = card_str[2:]
            
        for x in to_add:
            if (isinstance(x, Card) and (x.is_valid())):
                new_card = x
            elif isinstance(x, int):
                if ((x > -1) and (x < 52)):
                    new_card = Card(x)
                else:
                    return -1
            elif isinstance(x, str):
                new_card = Card(x)
                if new_card == -1:
                    return -1
            else:
                return -1

            # check to see if this new card is already in the hand
            new_index = new_card.get_index()
            for test_card in self.cards:
                if (test_card.get_index() == new_index):
                    return -1

            # if this card is in the deck, add it to the hand
            if (use_deck == None) or (use_deck.take_card(new_card) != -1):
                self.cards.append(new_card)
                self.suits[new_card.suit] += 1
                self.values[new_card.value] += 1
                self.vals_in_suit[new_card.suit] |= 1 << new_card.value
                self.all_values |= 1 << new_card.value

    def merge(self, other_hand):
        """ add the cards from another hand to this one """
        self.add_cards(other_hand.cards, None)

    def __len__(self):
        return len(self.cards)
