import playerStrategy
from boardItems import Property, Utility, Station
from random import randint
from util import *


class Player(object):

    def __init__(self):
        self.money = 200
        self.properties = []
        self.stations = []
        self.utilities = []
        self.in_jail = False
        self.rounds_in_jail = 0
        self.bankrupt = False
        self.latest_roll = None

    def get_preturn_blurb_info(self):

        land = {"properties": {}, "stations": [], "utilities": []}
        for p in self.properties:
            land["properties"].setdefault(p.format_coloured_name(), None)
            if p.num_houses() > 0:
                land['properties'][p.format_coloured_name()] = p.num_houses()

        for s in self.stations:
            land['stations'].append(s.name)

        for u in self.utilities:
            land['utilities'].append(u.name)

        return {"name": self.name, "money": self.money, "land": land}

    def pre_roll_actions(self):
        return

    def can_buy_property(self, tile):
        return tile.price <= self.money

    def buy_property(self, tile):
        if self.money < tile.price:
            display_action("Could not buy: %s, Not enough money! %s" % (tile.name))
        else:
            display_action("has brought: %s, current bal: %s" % (tile.name, self.money))
            self.money -= tile.price
            tile.owned_by = self

            if isinstance(tile, Property):
                self.properties.append(tile)
            elif isinstance(tile, Station):
                self.stations.append(tile)
            elif isinstance(tile, Utility):
                self.utilities.append(tile)

    def sell_property(self, tile):
        self.money += tile.price / 2
        tile.owned_by = None
        if isinstance(tile, Property):
            self.properties.remove(tile)
        elif isinstance(tile, Station):
            self.stations.remove(tile)
        elif isinstance(tile, Utility):
            self.utilities.remove(tile)

        display_action("has sold: %s, current bal: %s" %(tile.name, self.money))

    def pay_rent(self, tile):
        self.money -= tile.get_rent(self.latest_roll)
        tile.owned_by.money += tile.get_rent(self.latest_roll)
        display_action("has paid rent to: %s, current bal: %s" % (tile.owned_by.name, self.money))

    def get_asset_value(self):
        return self._get_variable_asset_variable(fuzzy_tolerance=0.0)

    def get_fuzzy_asset_value(self):
        """Monopoly rules state that you cannot make a decision about income tax before adding up
        Your assets, therefore we need a way to approximate our asset value to determine the decision

        """
        return self._get_variable_asset_variable(fuzzy_tolerance=0.5)

    def _get_variable_asset_variable(self, fuzzy_tolerance):

        # current problem with this method is that the margin gets bigger as the assets grow.
        # ie asset value is 50, a tolerance of 0.5 will give a randint between 25 and 75
        # but an asset value of 250 will give 125 and 375
        # perhaps it would work better to sum everything up and then randomise that
        # value within a range? Mathmatical analysis is needed here

        asset_value = 0
        asset_value += self.money

        def single_fuzzy_value(p):
            if fuzzy_tolerance > 0.0:
                return randint(int(p * (1 - fuzzy_tolerance)), int(p * (1 + fuzzy_tolerance)))
            else:
                return p

        for p in self.properties:
            if p.mortgaged:
                asset_value += single_fuzzy_value(p.mortgage_value)
            else:
                asset_value += single_fuzzy_value(p.price)

            if p.num_houses() > 0:
                asset_value += single_fuzzy_value(p.num_houses()*p.house_price)

        for su in self.stations+self.utilities:
            asset_value += single_fuzzy_value(su.price)

        return asset_value


    def find_mortgagable_properties(self):
        p = [p for p in self.properties if not p.mortgaged]
        s = [s for s in self.stations if not s.mortgaged]
        u = [u for u in self.utilities if not u.mortgaged]
        return  p + s + u

    def find_mortgaged_properties(self):
        p = [p for p in self.properties if p.mortgaged]
        s = [s for s in self.stations if s.mortgaged]
        u = [u for u in self.utilities if u.mortgaged]
        return p + s + u

    def send_to_jail(self):
        self.in_jail = True
        self.rounds_in_jail = 3

    def spend_turn_in_jail(self):
        if self.rounds_in_jail == 0:
            self.in_jail = False
        else:
            self.rounds_in_jail -= 1

    def get_out_of_jail(self):
        self.rounds_in_jail = 0
        self.in_jail = False

    def roll_dice(self):
        d1 = randint(1, 6)
        d2 = randint(1, 6)
        self.latest_roll = d1 + d2
        print self.name + " rolled: ", d1, d2
        return d1, d2


class AIPlayer(Player):

    def __init__(self, name):
        super(AIPlayer, self).__init__()
        self.name = "Player %s" %name
        self.strategy = playerStrategy.AlwaysBuyAndBuild
        self.mortgage_strategy = playerStrategy.LeastValueableFirstMortgaging

    def has_landed_on(self, tile, actions):

        if "Go to jail" in actions:
            self.in_jail = True
            return
        elif "Pay Rent" in actions:
            self.perform_action(tile, "Pay Rent")
        elif "Pay Tax" in actions:
            self.perform_action(tile, "Pay Tax")
        else:
            preferred = self.strategy.preferred_option(actions, tile, self)
            if preferred is not None and preferred in actions:
                self.perform_action(tile, preferred)
            else:
                self.perform_action(tile, self.strategy.normal_action(actions, tile, self))

    def do_mortgage(self):

        print "\t - Mortgaging properties"
        print "\t - %d properties to be mortgaged" % len(self.find_mortgagable_properties())

        to_mortgage = self.mortgage_strategy.mortgage_one(self)
        if to_mortgage is not None:
            to_mortgage.mortgaged = True
            self.money += to_mortgage.mortgage_value
            print "\t\t Mortgaged: ", to_mortgage.name, "  Bal: ", self.money


    def perform_action(self, tile, action):

        if action is None:
            return

        if action == "Buy":
            self.buy_property(tile)

        elif action == "Pay Tax":
            tax = tile.get_tax(self)
            self.pay_tax(tax)

        elif action == "Pay Rent":
            rent = tile.get_rent(self.latest_roll)
            print "\t\t - Have to pay rent of %d" %rent

            if self.money >= rent:
                self.pay_rent(tile)
            else:
                rent_paid = False
                while not rent_paid:

                    if len(self.find_mortgagable_properties()) == 0:
                        print "player couldn't pay rent and went bankrupt mortgaging houses"
                        self.bankrupt = True
                        break

                    self.perform_action(tile, "Mortgage")
                    if self.money >= rent:
                        self.pay_rent(tile)
                        rent_paid = True

        elif action == "Add House":
            print "\t - Buying house for %s" % tile.name
            tile.build_house()

        elif action == "Add Hotel":
            print "\t - Buying Hotel for %s" % tile.name
            tile.build_hotel()

        elif action == "Mortgage":
            self.do_mortgage()

        else:
            print "\t - Not doing anything"



    def pay_tax(self, tax):
        print "\t - is paying tax of: ", tax
        if isinstance(tax, int):
            print "\t - - Paid Super tax"
            self.money -= tax
        elif isinstance(tax, str):
            print "\t - - Paying income tax"
            fuzzy_value = self.get_fuzzy_asset_value()
            print "\t - - Estimating asset value at:", fuzzy_value
            if fuzzy_value < 2000:
                print "\t - - Paying flat rate "
                self.money -= 200
            else:
                av = int(self.get_asset_value() * 0.1)
                print "\t - - Paying percentage:", av
                self.money -= av


class HumanPlayer(Player):

    def __init__(self, name):
        super(HumanPlayer, self).__init__()
        self.name = "Player %s" %name

    def pre_roll_actions(self):

        action = None

        while action != "Roll Dice":

            actions = ["Roll Dice"]
            if self.find_mortgagable_properties() > 1:
                actions.append("Sell")
                actions.append("Mortgage")
                actions.append("Add House")
                actions.append("Add Hotel")

            if self.find_mortgaged_properties() > 1:
                actions.append("Unmortgage")

            choice_header("What would you like to do?")
            choice = self.display_actionlist(actions)
            action = actions[choice]

            if action == "Roll Dice":
                display_action("Rolling...")
                return

            properties = self.find_mortgagable_properties()
            choice_header("Please pick property to %s"% action)
            choice = self.display_actionlist([p.format_coloured_name() for p in properties])
            tile = properties[choice]

            if action == "Sell":
                print "\t - Selling %s" % tile.name
                self.sell_property(tile)

            elif action == "Add House":
                print "\t - Buying house for %s" % tile.name
                tile.build_house()

            elif action == "Add Hotel":
                print "\t - Buying Hotel for %s" % tile.name
                tile.build_hotel()

            elif action == "Mortgage":
                self.do_mortgage()

            elif action == "Unmortgage":
                self.do_mortgage()


    def has_landed_on(self, tile, actions):

        if len(actions) == 0:
            return

        if "Go to jail" in actions:
            self.in_jail = True
            return

        for x in actions:
            if "Pay" in x:
                action = actions[0]
                break
        else:
            choice_header("What would you like to do?")
            options = ['Nothing'] + actions
            choice = self.display_actionlist(options)
            action = options[choice]

        if action is None:
            return

        if action == "Buy":
            self.buy_property(tile)

        elif action == "Pay Tax":
            tax = tile.get_tax(self)
            self.pay_tax(tax)

        elif action == "Pay Rent":
            rent = tile.get_rent(self.latest_roll)
            display_action("Have to pay rent of %d" %rent)

            if self.money >= rent:
                self.pay_rent(tile)
            else:
                rent_paid = False
                while not rent_paid:

                    if len(self.find_mortgagable_properties()) == 0:
                        print "player couldn't pay rent and went bankrupt mortgaging houses"
                        self.bankrupt = True
                        break

                    self.do_mortgage()
                    if self.money >= rent:
                        print("You have enough to pay the rent. ")
                        self.pay_rent(tile)
                        rent_paid = True

        elif action == 'Nothing':
            display_action("Not doing anything")
        else:
            display_action("Not doing anything")

    def do_mortgage(self):

        properties = self.find_mortgagable_properties()
        print("What Property would you like to mortgage?")
        choice = self.display_actionlist([p.format_coloured_name() for p in properties])
        to_mortgage = properties[choice]

        if to_mortgage is not None:
            to_mortgage.mortgaged = True
            self.money += to_mortgage.mortgage_value

        display_action("Mortgaged: ", to_mortgage.name, "  Bal: ", self.money)


    def do_unmortgage(self):

        properties = self.find_mortgagable_properties()
        print("What Property would you like to unmortgage?")
        choice = self.display_actionlist([p.format_coloured_name() for p in properties])
        to_mortgage = properties[choice]

        if to_mortgage is not None:

            if self.money < to_mortgage.mortgage_value:
                print("\t - Could not unmortgage, not enough money!")

                to_mortgage.mortgaged = False
                self.money -= to_mortgage.mortgage_value

                display_action("Unortgaged: ", to_mortgage.name, "  Bal: ", self.money)

    def display_actionlist(self, actions):


        for i, item in enumerate(actions):
            print("%s) %s" %(str(i+1), item) )

        action = raw_input("\nPick Number: ").strip()

        try:
            action_int = int(action)
        except ValueError:
            print "Sorry, your choice was not a number. Please try again\n"
            return self.display_actionlist(actions)

        if action_int < 1 or action_int > len(actions):
            print ("Sorry, your choice was out of range. Please try again\n")
            return self.display_actionlist(actions)

        return action_int-1


    def pay_tax(self, tax):
        display_action("is paying tax of: ", tax)
        if isinstance(tax, int):
            display_action(" - Paid Super tax")
            self.money -= tax
        elif isinstance(tax, str):
            print "\t - - Paying income tax"

            print "Which tax would you like to pay?"
            which = self.display_actionlist(['Pay $200', "Pay 10%"])

            if which == 0:
                display_action(" - Paying flat rate ")
                self.money -= 200
            else:
                av = int(self.get_asset_value() * 0.1)
                display_action(" - Paying percentage:", av)
                self.money -= av
