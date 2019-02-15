import yaml
import os
from boardItems import Property, Station, Utility, Tax, Go, Jail, GoToJail, FreeParking, CommunityChest, Chance


class Board(object):

    def __init__(self, players):
        self.properties = []
        tiledata = self.get_tiles()
        self.gametiles = self.build_board(tiledata)
        print len(self.gametiles)

        self._player_locations = {}
        self.set_players_at_start(players)

    def get_tiles(self):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(path+"/propertylist.yml") as ymlfile:
            tiles = yaml.load(ymlfile)
        return tiles

    def get_config(self):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(path + "/conf.yml") as ymlfile:
            conf = yaml.load(ymlfile)
        return conf

    def build_board(self, tiles):

        conf = self.get_config()
        game_tiles = []

        for i, tiledata in enumerate(tiles):
            tiledata.update({"config": self.get_config()})
            if isinstance(tiledata, dict):
                if tiledata.get("type") is not None:
                    if tiledata.get("type") == "property":
                        game_tiles.append(Property(tiledata))

                    elif tiledata.get("type") == "utility":
                        game_tiles.append(Utility(tiledata))

                    elif tiledata.get("type") == "station":
                        game_tiles.append(Station(tiledata))

                    elif tiledata.get("type") == "tax":
                        game_tiles.append(Tax(tiledata))

                if tiledata.get("name") == "Community Chest":
                    game_tiles.append(CommunityChest())
                elif tiledata.get("name") == "Chance":
                    game_tiles.append(Chance())

                elif tiledata.get("name") == "Go":
                    game_tiles.append(Go())
                elif tiledata.get("name") == "Jail":
                    game_tiles.append(Jail())
                elif tiledata.get("name") == "Go To Jail":
                    game_tiles.append(GoToJail())
                elif tiledata.get("name") == "Free Parking":
                    game_tiles.append(FreeParking())


        return game_tiles

    def set_players_at_start(self, players):

        for p in players:
            print p
            self._player_locations.setdefault(p.name, 0)


    def advance_player(self, player, amount):

        playerloc = self._player_locations[player.name]

        playerloc += amount
        if playerloc >= len(self.gametiles):
            playerloc -= len(self.gametiles)
            if playerloc == 0:
                self.gametiles[0].player_landed_on(player)
            else:
                self.gametiles[0].player_gone_past(player)

        # go to jail implimented here, the player has no control over this
        if playerloc == 30:
            playerloc = 10
            player.send_to_jail()

        print "Player %s has advanced to %s" % (player.name, self.gametiles[playerloc].name)
        self._player_locations[player.name] = playerloc

        return playerloc

    def player_has_landed_on_go(self, player):
        player.money += self.gametiles[0].landed_on

    def player_has_gone_past_go(self, player):
        player.money += self.gametiles[0].go_amount

