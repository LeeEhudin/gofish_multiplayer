"""A module defining basic functions and generic classes for games"""

import abc

class Player(object):
    """Defines a Player for a game"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "{name}".format(**self.__dict__)

    def __repr__(self):
        return "Player(name={name!r})".format(**self.__dict__)

class Game(object, metaclass=abc.ABCMeta):
    """Defines a Game"""
    def __init__(self, players=None):
        if players:
            self.players = players
        else:
            self.players = []
        self.name = "Game"

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Game(players={players!r})".format(**self.__dict__)

    def add_player(self, player):
        """Adds a player to the game"""
        self.players.append(player)

    def get_player(self, name):
        """Returns the player with the same name as name, or None if none
        exists
        """
        for player in self.players:
            if player.name.lower() == name.lower():
                return player
        return None

    @abc.abstractmethod
    def play(self):
        """Interface for playing the game"""
        pass

def prompt(validator, prompt_msg="", error_msg=""):
    """Continually prompts the user for input until the validator
    validates it
    """
    val = input(prompt_msg)
    while True:
        try:
            if validator(val):
                break
        except Exception:
            pass
        print(error_msg, end="")
        val = input(prompt_msg)
    return val

def choice(choices):
    """Returns a numbered list of choices and prompts for a number in the
    list
    """
    for i, c in enumerate(choices):
        print("%d) %s" % (i, c))

    prompt_msg = "Please chose a number from the options list.\n"
    error_msg = "Please enter a number from 0-%d\n" % (len(choices)-1)
    validator = lambda val: int(val) in range(len(choices))
    return int(prompt(validator, prompt_msg, error_msg))
