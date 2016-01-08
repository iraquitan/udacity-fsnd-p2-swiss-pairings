#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach
import random


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


def delete_tournaments():
    """Remove all the tournaments records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE from tournaments;"
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
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    c.execute(query, (bleach.clean(name),))
    conn.commit()
    conn.close()


def unregister_player(player_id, tournament_id):
    """Removes a player from the tournament database.

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    query = "DELETE FROM tournament_players " \
            "WHERE player_id = %s AND tournament_id = %s;"
    c.execute(query, (bleach.clean(player_id), bleach.clean(tournament_id), ))
    conn.commit()
    conn.close()


def player_standings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
      tournament_id: the tournament id

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        t_id: the tournament's unique id (assigned by the database)
        p_id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT * FROM standings WHERE t_id = %s ORDER BY wins DESC;"
    c.execute(query, (bleach.clean(tournament_id),))
    ps = [(row[0], row[1], row[2], row[3], row[4]) for row in c.fetchall()]
    conn.commit()
    conn.close()
    return ps


def player_standings_omw(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
      tournament_id: the tournament id

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        t_id: the tournament' unique id (assigned by the database)
        p_id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        omw: the player's opponent match wins
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT * FROM standings_owm" \
            "WHERE t_id = %s ORDER BY wins DESC, omw DESC;"
    c.execute(query, (bleach.clean(tournament_id),))
    ps = [(row[0], row[1], row[2], row[3], row[4], row[5])
          for row in c.fetchall()]
    conn.commit()
    conn.close()
    return ps


def report_match(t_id, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      t_id: the tournament id
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO matches (tournament_id, winner_id, loser_id) " \
            "VALUES (%s, %s, %s)"
    c.execute(query, (bleach.clean(t_id), bleach.clean(winner),
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
    # TODO pairings when number of players is even but not factor of 2 (e.g 6)
    cp = count_players()
    swp = []
    already_paired = set([])
    if cp % 2 == 0:  # Assume even number of players
        ps = player_standings(tournament_id)
        for i in range(0, len(ps)-1):
            pid = ps[i][1]
            if set([pid]).issubset(already_paired):
                continue
            else:
                psi_opponents = get_players_opponents(pid, tournament_id)
                psi_opponent = random.choice(psi_opponents)
                while set([psi_opponent[0]]).issubset(already_paired):
                    psi_opponents.remove(psi_opponent)  # remove
                    psi_opponent = random.choice(psi_opponents)
                already_paired = already_paired.union([pid, psi_opponent[0]])
                swp.append((ps[i][1], ps[i][2],
                            psi_opponent[0], psi_opponent[1]))
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


def number_of_matches(num_of_players):
    """Finds out the necessary number of swiss pair rounds.

    Args:
      num_of_players: the number of players in tournament.
    Returns:
      num_of_rounds: necessary number of rounds to find winner.
    """
    num_of_rounds = 0
    while 2**num_of_rounds < num_of_players:
        num_of_rounds += 1
    return num_of_rounds


def get_players_opponents(player_id, tournament_id):
    """Add a player to participate on tournament.

    Assuming the tournament still have seats, subscribe player in tournament.

    Args:
      player_id: the player's id.
      tournament_id: the tournament' id.

    Returns:
      opponents: the player's possible opponents ids.
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT a.p_id AS a_id, b.p_id AS b_id, b.name AS b_name, a.wins " \
            "FROM standings AS a LEFT JOIN standings AS b " \
            "ON a.p_id <> b.p_id AND a.t_id = b.t_id " \
            "WHERE a.wins = b.wins AND a.p_id = %s AND a.t_id = %s;"
    c.execute(query, (bleach.clean(player_id), bleach.clean(tournament_id),))
    opponents = [(row[1], row[2]) for row in c.fetchall()]
    conn.commit()
    conn.close()
    return opponents
