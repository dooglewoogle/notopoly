from util import Colour

class Tile(object):
    def __init__(self, name):
        self.name = name

    def get_actions_for(self, player):
        raise NotImplementedError

    def format_coloured_name(self):
        try:
            return Colour[self.colourname] + self.name + Colour['END']
        except KeyError:
            return self.name
        except AttributeError:
            return self.name

class OwnableTile(Tile):

    def __init__(self, tiledata):
        super(OwnableTile, self).__init__(tiledata.get("name"))
        self.price = self.get_price(tiledata)
        self.owned_by = None
        self.mortgaged = False
        self._rent = tiledata.get("rent")
        self.mortgage_value = tiledata.get('mortgage_value')
        self.tiledata = tiledata
        self.colourname = tiledata.get("colour")


    def get_price(self, tiledata):
        return tiledata.get("price") * tiledata.get("config")["basePrice"]


    def get_actions_for(self, player):
        actions = []

        if self.owned_by is None and player.can_buy_property(self):
            actions.append("Buy")

        if self.owned_by is not None:
            if self.owned_by != player:
                actions.append("Pay Rent")
            else:
                actions.append("Mortgage")

        return actions

    def get_rent(self, *args):
        return self._rent

class Property(OwnableTile):

    def __init__(self, tiledata):
        super(Property, self).__init__(tiledata)
        self._houses = 0
        self.hotel = False
        self.house_price = tiledata.get("house_cost")

    def get_actions_for(self, player):
        actions = super(Property, self).get_actions_for(player)

        if self.owned_by is not None and self.owned_by == player:

            if self.can_build_hotel():
                actions.append("Add Hotel")

            elif self.can_build():
                actions.append("Add House")

        return actions

    def num_houses(self):
        return self._houses

    def get_rent(self, *args):

        if self.hotel:
            return self._rent.get("hotel")

        if self._houses == 0:
            return self._rent.get("property")
        else:
            houseIndex = max(self._houses - 1, 0)
            return self._rent.get("housePrices")[houseIndex]

    def can_build_hotel(self):
        return self._houses == 4 and self.can_build()

    def can_build(self):
        return self.owned_by.money >= self.house_price

    def build_house(self):
        if self._houses == 4:
            print "Could not build any more houses on this property"

        elif self.owned_by.money < self.house_price:
            print "Not enough money to build :("
        else:
            self._houses += 1
            self.owned_by.money -= self.house_price

    def build_hotel(self):
        if self._houses != 4:
            print "Not enough houses on this property to build hotel!"

        elif self.owned_by.money < self.house_price:
            print "Not enough money to build :("
        else:
            self._houses = 0
            self.hotel = True
            self.owned_by.money -= self.house_price

class Station(OwnableTile):

    def __init__(self, tiledata):
        super(Station, self).__init__(tiledata)

    def get_rent(self, *args):
        return 25 * len(self.owned_by.stations)


class Utility(OwnableTile):
    def __init__(self, tiledata):
        super(Utility, self).__init__(tiledata)

    def get_rent(self, roll):

        if len(self.owned_by.utilities) == 1:
            return 4*roll
        elif len(self.owned_by.utilities) == 2:
            return 10*roll
        else:
            print "------ No RENT"
            return 0


class Tax(Tile):

    def __init__(self, tiledata):
        super(Tax, self).__init__(tiledata.get('name'))
        self.name = tiledata.get('name')
        self.cost = tiledata.get("cost")

    def get_actions_for(self, player):
        return ["Pay Tax"]

    def get_tax(self, player):
        if "Super Tax" == self.name:
            return 100
        else:
            return "10 Percent or 200"


class Go(Tile):

    go_amount = 200
    landed_on = 400

    def __init__(self):
        super(Go, self).__init__("Go")

    def player_gone_past(self, player):
        print "%s has gone past go!" %player.name
        player.money += self.go_amount

    def player_landed_on(self, player):
        print "%s has landed on go!" %player.name
        player.money += self.landed_on

class Jail(Tile):
    def __init__(self):
        super(Jail, self).__init__("Jail")

    def get_actions_for(self, player):
        if player.in_jail:
            return ["Spend turn in jail", "Use get out of jail card"]
        else:
            return []

class FreeParking(Tile):
    def __init__(self):
        super(FreeParking, self).__init__("FreeParking")

class GoToJail(Tile):
    def __init__(self):
        super(GoToJail, self).__init__("Go To Jail")

    def get_actions_for(self, player):
        return ["Go to jail"]

class CommunityChest(Tile):
    def __init__(self):
        super(CommunityChest, self).__init__("Community Chest")

class Chance(Tile):
    def __init__(self):
        super(Chance, self).__init__("Chance")