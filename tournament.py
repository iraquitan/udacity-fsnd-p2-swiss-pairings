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
    query = "DELETE FROM matches;"
    c.execute(query)
    conn.commit()
    conn.close()


def delete_players():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE FROM players;"
    c.execute(query)
    conn.commit()
    conn.close()


def delete_tournaments():
    """Remove all the tournaments records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE FROM tournaments;"
    c.execute(query)
    conn.commit()
    conn.close()


def delete_byes():
    """Remove all the byes records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE FROM byes;"
    c.execute(query)
    conn.commit()
    conn.close()


def delete_tournament_players():
    """Remove all the tournament players records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE FROM tournament_players;"
    c.execute(query)
    conn.commit()
    conn.close()


def count_players():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    query = "SELECT COUNT(id) FROM players;"
    c.execute(query)
    cp = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return cp[0]


def count_tournament_players(tournament_id):
    """Returns the number of players currently assigned to tournament.

    Args:
      tournament_id: the tournament id to count players.
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT COUNT(id) FROM tournament_players " \
            "WHERE tournament_id = %s;"
    c.execute(query, (bleach.clean(tournament_id),))
    ctp = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return ctp[0]


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
    query = "SELECT * FROM standings_owm " \
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


def report_bye(t_id, player_id):
    """Records the a bye to a players.

    Args:
      t_id: the tournament id
      player_id: the player's id
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO byes (tournament_id, player_id) VALUES (%s, %s)"
    c.execute(query, (bleach.clean(t_id), bleach.clean(player_id),))
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
    cp = count_tournament_players(tournament_id)
    swp = []
    have_byes = set(get_tournament_byes(tournament_id))
    already_paired = set([])
    ps = player_standings(tournament_id)
    if cp % 2 == 0:
        bye_player = None
    else:
        players_ps = list(ps)
        if len(have_byes) is 0:  # If have_byes is empty, shuffle
            random.shuffle(players_ps)
        else:  # Search in
            players_ps.reverse()  # Search byes from the end of standings
        for p in players_ps:
            if len(have_byes) is 0:  # If have_byes is empty, add
                bye_player = (p[1], p[2])
                ps.remove(p)  # Remove bye player
                break
            else:  # If have_byes not empty, check if player already have bye
                if set([p[1]]).issubset(have_byes) is False:
                    bye_player = (p[1], p[2])
                    ps.remove(p)  # Remove bye player
                    break
    i = 0
    while len(swp) < len(ps)/2:
        # print("i = {}".format(i))
        pid = ps[i][1]
        curr_player = set([(ps[i][1], ps[i][2])])
        # if set([pid]).issubset(already_paired):
        if curr_player.issubset(already_paired):
            i += 1
            continue
        pid_opponents = get_player_opponents(pid, tournament_id)
        pairing_group = curr_player.union(set(pid_opponents))
        # Remove already paired
        pairing_group = pairing_group.difference(already_paired)

        mwins = 1
        while pairing_group == curr_player:
            if mwins > 1:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                      ">>>>>>>>>>>>>>>>>>>>>> My test!!!")
            pid_opponents = get_player_opponents(pid, tournament_id, mwins)
            pairing_group = curr_player.union(set(pid_opponents))
            # Remove already paired
            pairing_group = pairing_group.difference(already_paired)
            mwins += 1
        # Remove bye player from opponents
        try:
            if bye_player is not None:
                pairing_group = pairing_group.difference(set([bye_player]))
        except:
            print("Could not remove bye player {}".format(bye_player))

        pairing_group_cp = list(pairing_group)
        a_played_pairs = set([])
        pid_played_pairs = set([])
        for pi in list(pairing_group):
            pairing_group_cp.remove(pi)
            for pj in pairing_group_cp:
                if already_played(tournament_id, pi[0], pj[0]):
                    if pi[0] == pid or pj[0] == pid:
                        pid_played_pairs = pid_played_pairs.union(set([pi]))
                        pid_played_pairs = pid_played_pairs.union(set([pj]))
                    else:
                        a_played_pairs = a_played_pairs.union(set([pi]))
                        a_played_pairs = a_played_pairs.union(set([pj]))
        # Remove current player from pairing_group
        if len(pid_played_pairs) > 0:
            pid_played_pairs = pid_played_pairs.difference(curr_player)
        pairing_group = pairing_group.difference(curr_player)
        if len(a_played_pairs) == 0:
            if len(pid_played_pairs) > 0:
                if len(pairing_group.difference(pid_played_pairs)) > 0:
                    pairing_group = pairing_group.difference(pid_played_pairs)
        else:
            if len(pid_played_pairs) > 0:
                if len(pairing_group.difference(pid_played_pairs)) > 0:
                    pairing_group = pairing_group.difference(pid_played_pairs)
            if len(pairing_group.intersection(a_played_pairs)) > 0:
                pairing_group = pairing_group.intersection(a_played_pairs)


        pairing_group = list(pairing_group)
        random.shuffle(pairing_group)
        # Check if players already played
        try:
            if already_played(tournament_id,
                              list(curr_player)[0][0], pairing_group[0][0]):
                print("\n-----------------------------------------"
                      "------------------------>>> "
                      "Can't avoid {0} and {1} rematch".format(
                        list(curr_player)[0], pairing_group[0]))
        except:
            print("Some error found!!!!")
        # Update already paired players
        already_paired = already_paired.union(
                [list(curr_player)[0], pairing_group[0]])
        swp.append((list(curr_player)[0][0], list(curr_player)[0][1],
                    pairing_group[0][0], pairing_group[0][1]))
        i += 1
    swp_output = {'pairs': swp, 'byes': bye_player}
    return swp_output


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


def get_player_standings(tournament_id, player_id):
    """Returns a player standing in tournament.

    Args:
      tournament_id: the tournamento id.
      player_id: the player's id.

    Returns:
      player_standing: the player standings in the tournament
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT * FROM standings WHERE t_id = %s AND p_id = %s;"
    c.execute(query, (bleach.clean(tournament_id), bleach.clean(player_id),))
    players_id = [
        (row[0], row[1], row[2], row[3], row[4])
        for row in c.fetchall()
        ]
    conn.commit()
    conn.close()
    return players_id


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


def get_tournament_players_id(tournament_id):
    """Returns all tournament registered players id.

    Args:
      tournament_id: the tournament id to get players id.

    Returns:
      players_id: all players id in tournament.
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT player_id " \
            "FROM tournament_players WHERE tournament_id = %s;"
    c.execute(query, (bleach.clean(tournament_id),))
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
    query = "SELECT id FROM tournaments ORDER BY id;"
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


def get_player_opponents(player_id, tournament_id, m_wins=0):
    """Returns a player's id possible opponents.

    Args:
      player_id: the player's id.
      tournament_id: the tournament' id.
      same_wins: if should search opponents with same number of wins or not

    Returns:
      opponents: the player's possible opponents ids.
    """
    conn = connect()
    c = conn.cursor()
    if m_wins is 0:
        query = "SELECT a.p_id AS a_id, b.p_id AS b_id, b.name AS b_name, " \
                "a.wins FROM standings AS a LEFT JOIN standings AS b " \
                "ON a.p_id <> b.p_id AND a.t_id = b.t_id " \
                "WHERE a.wins = b.wins AND a.p_id = %s AND a.t_id = %s;"
        c.execute(query, (bleach.clean(player_id),
                          bleach.clean(tournament_id),))
    else:  # Get opponents with one or more win less than player
        query = "SELECT a.p_id AS a_id, b.p_id AS b_id, b.name AS b_name, " \
                "b.wins FROM standings AS a LEFT JOIN standings AS b " \
                "ON a.p_id <> b.p_id AND a.t_id = b.t_id " \
                "WHERE b.wins = a.wins-%s AND a.p_id = %s AND a.t_id = %s;"
        c.execute(query, (bleach.clean(m_wins), bleach.clean(player_id),
                          bleach.clean(tournament_id),))
    opponents = [(row[1], row[2]) for row in c.fetchall()]
    conn.commit()
    conn.close()
    return opponents

# def get_player_opponents(player_id, tournament_id, same_wins=True):
#     """Returns a player's id possible opponents.
#
#     Args:
#       player_id: the player's id.
#       tournament_id: the tournament' id.
#       same_wins: if should search opponents with same number of wins or not
#
#     Returns:
#       opponents: the player's possible opponents ids.
#     """
#     conn = connect()
#     c = conn.cursor()
#     if same_wins is True:
#         query = "SELECT a.p_id AS a_id, b.p_id AS b_id, b.name AS b_name, " \
#                 "a.wins FROM standings AS a LEFT JOIN standings AS b " \
#                 "ON a.p_id <> b.p_id AND a.t_id = b.t_id " \
#                 "WHERE a.wins = b.wins AND a.p_id = %s AND a.t_id = %s;"
#     else:  # Get opponents with one win less than player
#         query = "SELECT a.p_id AS a_id, b.p_id AS b_id, b.name AS b_name, " \
#                 "b.wins FROM standings AS a LEFT JOIN standings AS b " \
#                 "ON a.p_id <> b.p_id AND a.t_id = b.t_id " \
#                 "WHERE b.wins = a.wins-1 AND a.p_id = %s AND a.t_id = %s;"
#     c.execute(query, (bleach.clean(player_id), bleach.clean(tournament_id),))
#     opponents = [(row[1], row[2]) for row in c.fetchall()]
#     conn.commit()
#     conn.close()
#     return opponents


def decide_match(t_id, player1_id, player2_id):
    """Randomly decide the winner and loser of a match.

    Args:
      t_id: the tournament id
      player1_id:  the id number of the player who won
      player2_id:  the id number of the player who lost
    """
    players = [player1_id, player2_id]
    winner = random.choice(players)
    players.remove(winner)
    loser = players[0]
    report_match(t_id, winner, loser)


def get_tournament_byes(tournament_id):
    """Returns all byes in a tournament.

    Args:
      tournament_id: the tournament' id.

    Returns:
      byes: all tournament player' ids byes.
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT player_id FROM byes WHERE tournament_id = %s;"
    c.execute(query, (bleach.clean(tournament_id),))
    byes = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return byes


def already_played(tournament_id, player1_id, player2_id):
    """Returns true if players already played each other.

    Args:
      tournament_id: the tournament' id.
      player1_id: the player's 1 id.
      player2_id: the player's 2 id.

    Returns:
      answer: true if players already played, false otherwise.
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT exists(SELECT * FROM matches " \
        "WHERE (winner_id = %(p1)s AND loser_id = %(p2)s " \
            "AND tournament_id = %(t)s) " \
        "OR (loser_id = %(p1)s AND winner_id = %(p2)s " \
            "AND tournament_id = %(t)s));"
    c.execute(query, {'p1': bleach.clean(player1_id), 'p2': player2_id,
                      't': tournament_id})
    answer = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    return answer[0]
