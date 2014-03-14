#!/usr/bin/env python3.3
"""A program for playing a game of Go Fish"""

import os

from pytermgame import base, cards, multiplayer

class GoFishPlayer(cards.CardPlayer):
    """A player in a Go Fish game"""
    def __init__(self, name, hand=None, socket=None):
        super().__init__(name, hand)
        self.socket = socket
        self.matches = 0

    def send_mesg(self, mesg):
        """Send a message to the socket this player is connected to"""
        self.socket.sendall(mesg.encode("utf-8"))

    def get_mesg(self):
        """Get a message from the socket this player is connected to"""
        return self.socket.recv(1024).decode("utf-8")

class GoFish(cards.CardGame):
    """The game of Go Fish"""

    def pregame(self):
        print("Welcome to Go Fish!")

        name = input("What is your name?\n")

        prompt_msg = "Would you like to create a game or join a game?\n"
        error_msg = 'Please respond with "create" or "join" '
        validator = lambda val: val.lower() in ["create", "join"]
        response = base.prompt(validator, prompt_msg, error_msg)

        if response == "create":
            socket = multiplayer.mk_server("gofish", name)
            other_player_name = socket.recv(1024).decode("utf-8")
            self.add_player(GoFishPlayer(name))
            self.add_player(GoFishPlayer(other_player_name, None, socket))

            self.deal(7)
            for player in self.players:
                self.check_for_matches(player)
        elif response == "join":
            socket = None
            while True:
                game_list = []
                for filename in os.listdir("/tmp"):
                    if "gofish" in filename:
                        game_list.append(filename)

                game_list.append("reload games")
                choice = base.choice(game_list)
                if choice != len(game_list)-1:
                    socket = multiplayer.mk_client(game_list[choice])
                    break
            other_player_name = game_list[choice].split("_")[1]
            socket.sendall(name.encode("utf-8"))
            while True:
                data = socket.recv(1024).decode("utf-8")
                if not data:
                    break
                elif data.endswith("🃏"):
                    print(data[:-1])
                    prompt_msg = "What card do you want to guess?\n"
                    error_msg = ("Please enter a valid card value.\n"
                                 "Valid card values are 2-10, jack, queen, "
                                 "king, and ace.\n")
                    validator = (lambda val: val.lower() in cards.Card.VALUES)
                    asked_card_val = (base.prompt(validator, prompt_msg,
                                                  error_msg).lower())

                    prompt_msg = "Which player do you want to ask?\n"
                    error_msg = ("Please enter a valid player.\n"
                                 "Valid players are %s.\n" % other_player_name)
                    validator = (lambda val: val.lower() in
                                [other_player_name.lower()])
                    asked_player_name = base.prompt(validator, prompt_msg,
                                                    error_msg).lower()

                    result = "%s,%s" % (asked_card_val, asked_player_name)
                    socket.sendall(result.encode("utf-8"))
                    print()
                else:
                    print(data)
            socket.close()
            exit(0)

    def is_game_over(self):
        return not any([p.hand for p in self.players] + [self.deck])

    def move(self, player):
        self.print_to_all("It's %s's turn!\n" % player.name)
        if player.socket:
            player.send_mesg("Your hand is:\n%s" % player.hand)
            player.send_mesg("🃏")
            asked_card_val, asked_player_name = player.get_mesg().split(",")
            asked_player = self.get_player(asked_player_name)
        else:
            print("Your hand is:\n%s" % player.hand)

            prompt_msg = "What card do you want to guess?\n"
            error_msg = ("Please enter a valid card value.\nValid card values are "
                         "2-10, jack, queen, king, and ace.\n")
            validator = lambda val: val.lower() in cards.Card.VALUES
            asked_card_val = base.prompt(validator, prompt_msg, error_msg).lower()

            prompt_msg = "Which player do you want to ask?\n"
            error_msg = ("Please enter a valid player.\nValid players are %s.\n" %
                         ", ".join(str(p) for p in self.players if p != player))
            validator = lambda val: val.lower() in [str(p).lower() for
                                                    p in self.players if
                                                    p != player]
            asked_player_name = base.prompt(validator, prompt_msg,
                                                       error_msg).lower()
            asked_player = self.get_player(asked_player_name)
            print()

        self.print_to_all("%s, do you have any %ss?" %
                          (asked_player, asked_card_val))

        matches = []
        for card in asked_player.hand:
            if card.value == asked_card_val:
                matches.append(card)
                asked_player.hand.remove_card(card)

        player.hand += matches
        if len(matches) == 0:
            self.print_to_all("%s didn't have any %ss\nGo fish!" %
                              (asked_player, asked_card_val))
            if self.deck:
                player.hand.add_card(next(self.deck))
            else:
                self.print_to_all("There are no cards left in the deck")
        elif len(matches) == 1:
            self.print_to_all("%s gave %s one %s" %
                              (asked_player, player, asked_card_val))
        elif len(matches) == 2:
            self.print_to_all("%s gave %s two %ss" %
                              (asked_player, player, asked_card_val))
        elif len(matches) == 3:
            self.print_to_all("%s gave %s three %ss" %
                              (asked_player, player, asked_card_val))

        self.check_for_matches(player)

    def postgame(self):
        winners = [player.name for player in self.players if player.matches ==
                   max([player.matches for player in self.players])]
        if len(winners) == 1:
            self.print_to_all("The winner is %s" % winners[0])
        else:
            self.print_to_all("The winners are %s, and %s" %
                  (", ".join(winners[:-1]), winners[-1]))
        for player in self.players:
            if player.socket:
                player.send_mesg("")
                player.socket.close()
                os.remove(player.socket.getsockname())

    def check_for_matches(self, player):
        """Checks for sets of four matching cards in the player's hand"""
        for value in cards.Card.VALUES:
            if [card.value for card in player.hand].count(value) == 4:
                for suit in cards.Card.SUITS:
                    player.hand.remove_card(cards.Card(value, suit))
                player.matches += 1
                self.print_to_all("%s put down four %ss" % (self.name, value))

    def print_to_all(self, mesg):
        """Prints mmesg to all players"""
        for player in self.players:
            if player.socket:
                player.send_mesg(mesg)
            else:
                print(mesg)

GoFish().play()
