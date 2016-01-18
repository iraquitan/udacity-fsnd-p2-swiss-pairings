#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def test_delete_matches():
    delete_matches()
    print "1. Old matches can be deleted."


def test_delete():
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()
    print "2. Player records can be deleted."


def test_count():
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()
    c = count_players()
    if c == '0':
        raise TypeError(
            "count_players() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, count_players should return zero.")
    print "3. After deleting, count_players() returns zero."


def test_register():
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()
    register_player("Chandra Nalaar")
    c = count_players()
    if c != 1:
        raise ValueError(
            "After one player registers, count_players() should be 1.")
    print "4. After registering a player, count_players() returns 1."


def test_register_count_delete():
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()
    register_player("Markov Chaney")
    register_player("Joe Malik")
    register_player("Mao Tsu-hsi")
    register_player("Atlanta Hope")
    c = count_players()
    if c != 4:
        raise ValueError(
            "After registering four players, count_players should be 4.")
    delete_players()
    c = count_players()
    if c != 0:
        raise ValueError("After deleting, count_players should return zero.")
    print "5. Players can be registered and deleted."


def test_standings_before_matches():
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()
    register_player("Melpomene Murray")
    register_player("Randy Schwartz")
    create_tournament(num_of_players=2)
    players_ids = get_players_id()
    reg_tournaments = get_tournaments_id()
    for i in range(2):
        subscribe_player(players_ids[i], reg_tournaments[-1])

    standings = player_standings(reg_tournaments[-1])
    if len(standings) < 2:
        raise ValueError("Players should appear in player_standings even "
                         "before they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 5:
        raise ValueError("Each player_standings row should have five columns.")
    [(t_id, id1, name1, wins1, matches1),
     (t_id, id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in "
                         "standings, even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no " \
          "matches."


def test_report_matches():
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()
    register_player("Bruno Walton")
    register_player("Boots O'Neal")
    register_player("Cathy Burton")
    register_player("Diane Grant")
    create_tournament(num_of_players=4)
    players_ids = get_players_id()
    reg_tournaments = get_tournaments_id()
    for i in range(4):
        subscribe_player(players_ids[i], reg_tournaments[-1])

    standings = player_standings(reg_tournaments[-1])
    [id1, id2, id3, id4] = [row[1] for row in standings]
    report_match(reg_tournaments[-1], id1, id2)
    report_match(reg_tournaments[-1], id3, id4)
    standings = player_standings(reg_tournaments[-1])
    for (t, i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def test_pairings():
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()
    register_player("Twilight Sparkle")
    register_player("Fluttershy")
    register_player("Applejack")
    register_player("Pinkie Pie")
    create_tournament(num_of_players=4)
    players_ids = get_players_id()
    reg_tournaments = get_tournaments_id()
    for i in range(4):
        subscribe_player(players_ids[i], reg_tournaments[-1])
    standings = player_standings(reg_tournaments[-1])
    [id1, id2, id3, id4] = [row[1] for row in standings]
    report_match(reg_tournaments[-1], id1, id2)
    report_match(reg_tournaments[-1], id3, id4)
    pairings = swiss_pairings(reg_tournaments[-1])
    if len(pairings['pairs']) != 2:
        raise ValueError(
            "For four players, swiss_pairings should return two pairs.")
    [(pid1, pname1, pid2, pname2),
     (pid3, pname3, pid4, pname4)] = pairings['pairs']
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def test_new_database():
    # Delete records
    delete_matches()
    delete_byes()
    delete_tournament_players()
    delete_players()
    delete_tournaments()

    # Register players to database
    register_player("Twilight Sparkle")
    register_player("Fluttershy")
    register_player("Applejack")
    register_player("Pinkie Pie")
    register_player("Iraquitan Filho")
    register_player("Alexandre Gomes")
    register_player("Adan Salazar")
    register_player("Djenifer Paula")
    register_player("Kevin Cordeiro")
    register_player("Yugi Muto")
    register_player("Ash Ketchum")
    register_player("Stefani Karoline")
    register_player("Jose Filho")
    register_player("Ney Junior")
    register_player("Hedurado Cordeiro")
    register_player("Fredson Santos")
    register_player("Yoshio")
    register_player("Wallace Lira")
    players_ids = get_players_id()

    tournaments_n_players = [4, 6, 7, 8, 9, 16, 17, 18]
    for tournament_n in tournaments_n_players:
        byes = []
        print("\n\n{:#^64}".format('#'))
        title = "Tournament with {} players".format(tournament_n)
        print("{:#^64}".format(title))
        print("{:#^64}".format('#'))
        create_tournament(num_of_players=tournament_n)
        reg_tournaments = get_tournaments_id()
        random.shuffle(players_ids)  # Shuffle players
        for i in range(tournament_n):
            subscribe_player(players_ids[i], reg_tournaments[-1])
        n_matches = number_of_matches(count_tournament_players(
                reg_tournaments[-1]))
        for match in range(n_matches):
            print("\nMatch {}".format(match+1))
            pairings = swiss_pairings(reg_tournaments[-1])
            if len(pairings['pairs']) != tournament_n / 2:
                raise ValueError(
                    "For {0} players, swiss_pairings "
                    "should return {1} pairs.".format(tournament_n,
                                                      tournament_n/2))
            print('Swiss pairings for match {}:'.format(match + 1))
            for pairs in pairings['pairs']:
                print("\t{}".format(pairs))
                decide_match(reg_tournaments[-1], pairs[0], pairs[2])
            if tournament_n % 2 == 0 and pairings['byes'] is not None:
                raise ValueError("For even number of players, swiss pairings "
                                 "should return no bye.")
            print('Byes for match {}:'.format(match + 1))
            print("\t{}".format(pairings['byes']))
            if tournament_n % 2 != 0 and pairings['byes'] is None:
                raise ValueError("For odd number of players, swiss pairings "
                                 "should return a bye per round.")
            if pairings['byes'] is not None:
                if pairings['byes'] in byes:
                    raise ValueError("The same player should not receive more "
                                     "than one bye per tournament.")
                report_bye(reg_tournaments[-1], pairings['byes'][0])
                byes.append(pairings['byes'])
            print('Match {} results:'.format(match + 1))
            if match + 1 == n_matches:
                standings = player_standings_omw(reg_tournaments[-1])
                print("|{0:_^8}|{1:_^8}|{2:_^20}|{3:_^6}|{4:_^9}|{5:_^5}|".format(
                        't-id', 'p-id', 'name', 'wins', 'matches', 'OMW'))
                for st in standings:
                    print("|{0:^8}|{1:^8}|{2:^20}|{3:^6}|{4:^9}|{5:^5}|".format(
                            st[0], st[1], st[2], st[3], st[4], st[5]))
            else:
                standings = player_standings(reg_tournaments[-1])
                print("|{0:_^8}|{1:_^8}|{2:_^20}|{3:_^6}|{4:_^9}|".format(
                        't-id', 'p-id', 'name', 'wins', 'matches'))
                for st in standings:
                    print("|{0:^8}|{1:^8}|{2:^20}|{3:^6}|{4:^9}|".format(
                            st[0], st[1], st[2], st[3], st[4]))
        if standings[0][3] > standings[1][3]:
            print("\nWinner is {0}:\n"
                  "\tWins: {1}"
                  "\tMatches: {2}"
                  "\tOMW: {3}".format((standings[0][1], standings[0][2]),
                                      standings[0][3], standings[0][4],
                                      standings[0][5]))
        else:
            if standings[0][5] > standings[1][5]:
                print("\nWinner by 'TIEBREAK' is {0}:\n"
                      "\tWins: {1}"
                      "\tMatches: {2}"
                      "\tOMW: {3}".format((standings[0][1], standings[0][2]),
                                          standings[0][3], standings[0][4],
                                          standings[0][5]))
            else:
                print("\nNo Winner by 'TIEBREAK'!!!")

    print "9. Tests with 4, 6, 8, 9, 16, 17 and 18 number of players passed."

if __name__ == '__main__':
    test_delete_matches()
    test_delete()
    test_count()
    test_register()
    test_register_count_delete()
    test_standings_before_matches()
    test_report_matches()
    test_pairings()
    # Custom tests
    test_new_database()
    print "Success!  All tests pass!"


