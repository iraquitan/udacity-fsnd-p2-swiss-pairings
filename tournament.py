#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach
import re


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def delete_matches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE from matches;"
    c.execute(query)
    conn.commit()
    conn.close()


def delete_players():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE from players;"
    c.execute(query)
    conn.commit()
    conn.close()


def count_players():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    query = "SELECT COUNT(id) from players;"
    c.execute(query)
    cp = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return cp[0]


def register_player(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    fname = re.findall('\w+', name)[0]
    lname = re.findall('\w+', name)[-1]
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO players (first_name, last_name) VALUES (%s, %s)"
    c.execute(query, (bleach.clean(fname), bleach.clean(lname),))
    conn.commit()
    conn.close()


def player_standings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT * FROM standings;"
    c.execute(query)
    ps = [(row[0], row[1]+' '+row[2], row[3], row[4]) for row in c.fetchall()]
    conn.commit()
    conn.close()
    return ps


def report_match(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO matches (winner_id, loser_id) VALUES (%s, %s)"
    c.execute(query, (bleach.clean(winner), bleach.clean(loser),))
    conn.commit()
    conn.close()
 
 
def swiss_pairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    cp = count_players()
    if cp % 2 == 0:  # Assume ever number of players
        ps = player_standings()
        # TODO Make swiss pairings
        # for psi in ps:
        #     psi
