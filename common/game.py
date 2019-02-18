from player import AIPlayer, HumanPlayer
from board import Board
from random import randint
from time import sleep
from util import *

class Game(object):

    turn_delay = 0.0

    def __init__(self, output, num_players=8):

        self.output = output
        self.players = [AIPlayer(x + 1) for x in range(num_players)]
        #self.players = [AIPlayer('Robit'), HumanPlayer("Bob")]
        self.output(self.players)
        self.board = Board(self.players)

        self.start_game()


    def start_game(self):
        self.game_in_progress = True

        while self.game_in_progress:
            for player in self.players:
                print ""
                doubles_rolled = 0

                if player.bankrupt is True:
                    self.players.remove(player)
                    print "%s is bankrupt!" % player.name

                if len(self.players) < 2:
                    self.game_in_progress = False

                player_blurb = player.get_preturn_blurb_info()
                player_pos = self.board.get_player_position(player)
                player_blurb.update({"position": player_pos.format_coloured_name()})
                display_turnstart_blurb(**player_blurb)
                player.pre_roll_actions()
                
                # initial roll
                roll = player.roll_dice()
                rolled_doubles = roll[0] == roll[1]
                sleep(self.turn_delay)

                if not rolled_doubles:
                    self.take_action(player, roll)
                else:
                    while rolled_doubles:
                        doubles_rolled += 1
                        if doubles_rolled == 3:
                            print "\nPlayer has rolled 3 doubles and is going to jail!"
                            player.send_to_jail()
                            break
                        self.take_action(player, roll)

                        roll = player.roll_dice()
                        rolled_doubles = roll[0] == roll[1]
                    sleep(self.turn_delay)
                sleep(self.turn_delay)

        print "Game over!"
        print "%s won" %self.players[0].name

    def take_action(self, player, roll):

        rolled_doubes = roll[0] == roll[1]
        dice_result = sum(roll)

        if player.in_jail:
            print "%s is in Jail!" % player.name
            player.spend_turn_in_jail()
            if rolled_doubes:
                player.get_out_of_jail()
        else:
            number = self.board.advance_player(player, dice_result)
            tile = self.board.gametiles[number]
            try:
                actions = tile.get_actions_for(player)
                print "\tActions:", actions
                player.has_landed_on(tile, actions)
            except NotImplementedError, e:
                pass
        display_turnend()


