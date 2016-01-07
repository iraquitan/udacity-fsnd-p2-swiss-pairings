INSERT INTO players (first_name, last_name) VALUES ('Iraquitan', 'Filho');
INSERT INTO players (first_name, last_name) VALUES ('Djenifer', 'Paula');
INSERT INTO players (first_name, last_name) VALUES ('Alexandre', 'Gomes');
INSERT INTO players (first_name, last_name) VALUES ('Adan', 'Salazar');

-- SELECT players.id, players.first_name, players.last_name,
--       (SELECT count(matches.id)
--        FROM matches
--        WHERE players.id = matches.winner_id) AS wins,
--       (SELECT count(matches.id)
--        FROM matches
--        WHERE players.id = matches.winner_id
--              OR players.id = matches.loser_id) AS matches_num
--     FROM players LEFT JOIN matches
--          ON matches.id = players.id
--     GROUP BY players.id
--     ORDER BY  wins DESC;

-- DROP VIEW standings;

-- DELETE FROM matches;
INSERT INTO matches (winner_id, loser_id) VALUES (98, 100);
INSERT INTO matches (winner_id, loser_id) VALUES (99, 98);
INSERT INTO matches (winner_id, loser_id) VALUES (1, 4);
-- INSERT INTO matches (winner_id, loser_id) VALUES (2, 3);
-- INSERT INTO matches (winner_id, loser_id) VALUES (2, 1);
-- INSERT INTO matches (winner_id, loser_id) VALUES (3, 4);

-- SELECT * from standings;

-- SELECT count(id) FROM players;

SELECT a.id AS a_id, b.id AS b_id, a.wins
from standings AS a JOIN standings AS b
        ON a.id < b.id
WHERE a.wins = b.wins;


SELECT * FROM (SELECT a.id AS a_id, b.id AS b_id, a.wins
               from standings AS a
                 LEFT JOIN standings AS b ON a.id < b.id
               WHERE a.wins = b.wins) AS swiss;

-- OMW (Opponent Match Wins)
SELECT a.id AS a_id, sum(o.wins) AS OMW
FROM standings AS a
  JOIN matches ON a.id = matches.winner_id OR a.id = matches.loser_id
  JOIN standings AS o
    ON a.id <> o.id AND (o.id = matches.winner_id OR o.id = matches.loser_id)
GROUP BY a.id;

-- OMP (Opponent Match Percentage)
SELECT a.id AS a_id, sum(o.wins::FLOAT/(o.matches_num))/count(o.wins) AS OMP
FROM standings AS a
  JOIN matches ON a.id = matches.winner_id OR a.id = matches.loser_id
  JOIN standings AS o
    ON a.id <> o.id AND (o.id = matches.winner_id OR o.id = matches.loser_id)
GROUP BY a.id;

-- Check if value exist on column
SELECT exists(SELECT * FROM players WHERE id = 97);

-- DROP TRIGGER check_player_trg ON matches;
