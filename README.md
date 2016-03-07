# PROJECT 2 - Swiss Pairings Tournament
This project provides code to store players and matches in database and provide functions to do swiss pairings.

## Table of contents
* [Requirements](#requirements)
* [Quick start](#quick-start)
* [Creator](#creator)

## Requirements
* Python 2.7
* Git
* [Vagrant](https://www.vagrantup.com)
* [VirtualBox](https://www.virtualbox.org)

## Quick start
* Clone the repo: `git clone https://github.com/iraquitan/vagrant-trusty64-python-web.git` if you don't already have a vagrant VM configured with PostgreSQL.
* Change directory to the newly cloned repo.
* Clone this repo `git clone https://github.com/iraquitan/udacity-fsnd-p2-swiss-pairings.git tournament`.
* Run the following code on terminal: `vagrant up` to setup virtual machine.
* Run the following code on terminal: `vagrant ssh` to connect to the virtual machine using ssh.
* Run the following code on terminal: `cd /vagrant/tournament/` to change directory to this project.
* Run the following code on terminal: `dropdb --if-exists tournament` to drop tournament database if already exists.
* Run the following code on terminal: `createdb tournament` to create tournament database.
* Run the following code on terminal: `psql tournament -f /vagrant/tournament/tournament.sql` to feed the tournament database with tables and rules in the tournament.sql file.
* To test, run the following on terminal: `python /vagrant/tournament/tournament_test.py`.
* This project has extra credits, listed above:
    - Prevent rematches between players.
    - Don’t assume an even number of players. If there is an odd number of players, assign one player a “bye” (skipped round). A bye counts as a free win. A player should not receive more than one bye in a tournament.
    - When two players have the same number of wins, rank them according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
    - Support more than one tournament in the database, so matches do not have to be deleted between tournaments. This will require distinguishing between “a registered player” and “a player who has entered in tournament #123”, so it will require changes to the database schema.

## Creator
**Iraquitan Cordeiro Filho**

* <https://twitter.com/iraquitan_filho>
* <https://github.com/iraquitan>
