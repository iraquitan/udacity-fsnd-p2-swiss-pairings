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
    # name_words = re.findall('\w+', name)
    # fname = name_words[0]
    # if len(name_words) > 1:
    #     lname = name_words[-1]
    # else:
    #     lname = ""
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    c.execute(query, (bleach.clean(name),))
    conn.commit()
    conn.close()


def player_standings(tournament_id):
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
    query = "SELECT * FROM standings WHERE t_id = %s ORDER BY wins DESC;"
    c.execute(query, (bleach.clean(tournament_id),))
    # ps = [(row[0], row[1]+' '+row[2], row[3], row[4]) for row in c.fetchall()]
    ps = [(row[0], row[1], row[2], row[3], row[4]) for row in c.fetchall()]
    conn.commit()
    conn.close()
    return ps


def report_match(tournament_id, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO matches (tournament_id, winner_id, loser_id) " \
            "VALUES (%s, %s, %s)"
    c.execute(query, (bleach.clean(tournament_id), bleach.clean(winner),
                      bleach.clean(loser),))
    conn.commit()
    conn.close()
 
 
def swiss_pairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
      tournament_id: the tournament id.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    cp = count_players()
    swp = []
    if cp % 2 == 0:  # Assume even number of players
        ps = player_standings(tournament_id)
        for i in range(0, len(ps)-1, 2):
            swp.append((ps[i][1], ps[i][2], ps[i+1][1], ps[i+1][2]))
    else:
        raise Exception('Number of players should be even.')
    return swp


def create_tournament(num_of_players):
    """Add a tournament to the database.

    The database assigns a unique serial id number for the tournament.

    Args:
      num_of_players: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO tournaments (num_of_players) VALUES (%s)"
    c.execute(query, (bleach.clean(num_of_players),))
    conn.commit()
    conn.close()


def get_players_id():
    """Returns all registered players id.

    Returns:
      players_id: all players id.
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT id FROM players;"
    c.execute(query)
    players_id = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return players_id


def get_tournaments_id():
    """Returns all registered tournament ids.

    Returns:
      tournaments_id: all tournament ids.
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT id FROM tournaments;"
    c.execute(query)
    tournaments_id = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return tournaments_id


def subscribe_player(player_id, tournament_id):
    """Add a player to participate on tournament.

    Assuming the tournament still have seats, subscribe player in tournament.

    Args:
      player_id: the player's id.
      tournament_id: the tournament' id.
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO tournament_players (player_id, tournament_id) " \
            "VALUES (%s, %s)"
    c.execute(query, (bleach.clean(player_id), bleach.clean(tournament_id),))
    conn.commit()
    conn.close()
