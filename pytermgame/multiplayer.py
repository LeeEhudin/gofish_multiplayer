"""A module defining functions for playing multiplayer games"""

import abc
import socket
import os
import os.path

from . import base

def mk_server(game_name, player_name):
    """Returns a serer for a game"""
    socket_name = ("/tmp/%s_%s_%s" % (game_name, player_name, os.getpid()))

    if os.path.exists(socket_name):
        os.remove(socket_name)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_name)
    server.listen(1)

    conn, addr = server.accept()

    return conn

def mk_client(socket_name):
    """Returns a client for a game"""
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect("/tmp/%s" % socket_name)

    return client
