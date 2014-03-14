"""A module defining functions for playing card games"""

import abc
import bisect
import collections.abc
import itertools
import random

from . import base

class Card(object):
    """Defines a Card class for easy access to a card's suit and value"""
    VALUES = ("ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
              "jack", "queen", "king")
    SUITS = ("spades", "hearts", "diamonds", "clubs")
    _value_aliases = {"ace":"A", "jack":"J", "queen":"Q", "king":"K"}
    _suit_aliases = {"spades":"♠", "hearts":"♥", "diamonds":"♦", "clubs":"♣"}

    def __init__(self, value, suit):
        short_suits = {suit[0]:suit for suit in Card.SUITS}

        if isinstance(value, int):
            if value in range(1, len(Card.VALUES)+1):
                self.value = Card.VALUES[value-1]
            else:
                raise ValueError("%d is not a valid value for a card." % value)
        elif str(value).lower() in Card.VALUES:
            self.value = str(value).lower()
        else:
            raise ValueError("%s is not a valid value for a card." % value)

        if str(suit).lower() in short_suits:
            self.suit = short_suits[str(suit).lower()]
        elif str(suit).lower() in Card.SUITS:
            self.suit = str(suit).lower()
        else:
            raise ValueError("%s is not a valid suit for a card." % suit)

    def __eq__(self, other):
        if (isinstance(other, Card) and
            self.value == other.value and self.suit == other.suit):
            return True
        else:
            return False

    def __neq__(self, other):
        return not self == other

    def __lt__(self, other):
        if Card.VALUES.index(self.value) < Card.VALUES.index(other.value):
            return (Card.VALUES.index(self.value) <
                    Card.VALUES.index(other.value))
        else:
            return Card.SUITS.index(self.suit) < Card.SUITS.index(other.suit)

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    def __str__(self):
        return "{:1}{:1}".format(
            Card._value_aliases.get(self.value, self.value),
            Card._suit_aliases.get(self.suit, self.suit))

    def __repr__(self):
        return "Card(value={value!r}, suit={suit!r})".format(**self.__dict__)

class Deck(collections.abc.Sized, collections.abc.Iterator):
    """Defines a Deck class to store cards"""
    def __init__(self, shuffled=True):
        self.cards = [Card(value, suit) for
                     suit in Card.SUITS for value in Card.VALUES]
        if shuffled:
            self.shuffle()

    def __repr__(self):
        return repr(', '.join(repr(card) for card in self.cards))

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return self.deal_cards()

    def __next__(self):
        return next(self.deal_cards())

    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)

    def deal_cards(self):
        """A generator that deals out cards"""
        if not self.cards:
            raise IndexError("Deck is empty.")
        for card in list(self.cards):
            self.cards.remove(card)
            yield card

class Hand(collections.abc.Sized, collections.abc.Container,
           collections.abc.Iterable):
    """Defines a Hand class to store Player's hands"""
    def __init__(self, cards=None, sort_by_val=True):
        self.cards = []
        if sort_by_val:
            self._sorted_by_val = True
        else:
            self._sorted_by_val = False
        self._keys = []

        if cards:
            for card in cards:
                self.add_card(card)

    def __add__(self, other):
        for card in other:
            self.add_card(card)
        return self

    def __eq__(self, other):
        if (isinstance(other, Hand) and
                sorted(self.cards) == sorted(other.cards)):
            return True
        else:
            return False

    def __neq__(self, other):
        return not self == other

    def __len__(self):
        return len(self.cards)

    def __contains__(self, item):
        return item in self.cards

    def __iter__(self):
        for card in self.cards:
            yield card

    def __repr__(self):
        return repr(', '.join(repr(card) for card in self.cards))

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

    @property
    def sorting(self):
        """Returns a string identifying how the Hand is sorted"""
        if self._sorted_by_val:
            return "value"
        else:
            return "suit"

    def add_card(self, card):
        """Add a card to the Hand"""
        key = 0
        if self._sorted_by_val:
            key = (Card.VALUES.index(card.value)*4 +
                   Card.SUITS.index(card.suit))

        else:
            key = (Card.SUITS.index(card.suit)*13 +
                   Card.VALUES.index(card.value))
        index = bisect.bisect(self._keys, key)
        self._keys.insert(index, key)
        self.cards.insert(index, card)

    def remove_card(self, card):
        """Removes a card from the Hand"""
        self.cards.remove(card)

    def sort_by_value(self):
        """Sorts the hand by value"""
        if not self._sorted_by_val:
            self._sorted_by_val = True

            temp_hand = self.cards
            self.cards = []
            self._keys = []

            for card in temp_hand:
                self.add_card(card)

    def sort_by_suit(self):
        """Sorts the hand by suit"""
        if self._sorted_by_val:
            self._sorted_by_val = False

            temp_hand = self.cards
            self.cards = []
            self._keys = []

            for card in temp_hand:
                self.add_card(card)

class CardPlayer(base.Player):
    """Defines a Player for a card game"""
    def __init__(self, name, hand=None):
        super().__init__(name)
        if hand:
            self.hand = hand
        else:
            self.hand = Hand()

    def __add__(self, other):
        return self.hand + other

    def __iadd__(self, other):
        self.hand += other
        return self

    def __repr__(self):
        return ("CardgamePlayer(name={name!r}, "
                "hand={hand!r})".format(**self.__dict__))

    def add_card(self, card):
        """Add a card to the player's hand"""
        self.hand.add_card(card)

class CardGame(base.Game, metaclass=abc.ABCMeta):
    """Defines a card game"""
    def __init__(self, players=None):
        super().__init__(players)
        self.name = "CardGame"
        self.deck = Deck()

    def __repr__(self):
        return ("Cardgame(players={players!r}, "
                "deck={deck!r})".format(**self.__dict__))

    def deal(self, num_cards):
        """Deals out num_cards to each player"""
        for _ in range(num_cards):
            for player in self.players:
                try:
                    player.add_card(next(self.deck))
                except StopIteration:
                    raise IndexError("Deck is empty.")

    def pregame(self):
        """Function exectuted before the main game logic"""
        pass

    @abc.abstractmethod
    def move(self, player):
        """Interface for defining a player's move"""
        pass

    @abc.abstractmethod
    def is_game_over(self):
        """Interface for determining whether the game is over"""
        return False

    def postgame(self):
        """Function exectuted after the main game logic"""
        pass

    def play(self):
        """Defines the flow of execution in a card games"""
        self.pregame()
        player_cycle = itertools.cycle(self.players)
        self.move(next(player_cycle))
        while not self.is_game_over():
            self.move(next(player_cycle))
        self.postgame()
