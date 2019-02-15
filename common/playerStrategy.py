class Strategy(object):
    pass

class AllwaysMortgage(Strategy):

    @staticmethod
    def preferred_option(actions, tile, player):
        return "Mortgage"


    @staticmethod
    def normal_action(actions, tile, player):
        if "Buy" in actions and player.can_buy_property(tile):
            return "Buy"

class AlwaysBuyAndBuild(Strategy):
    @staticmethod
    def preferred_option(actions, tile, player):
        if "Buy" in actions and player.can_buy_property(tile):
            return "Buy"
        elif "Add hotel" in actions:
            return "Add Hotel"
        elif "Add House" in actions:
            return "Add House"


    @staticmethod
    def normal_action(actions, tile, player):
        return None


class LeastValueableFirstMortgaging(Strategy):

    @staticmethod
    def least_valuable(things):
        least = None

        for t in things:

            if not t.mortgaged:
                if least is None:
                    least = t
                if t.mortgage_value < least:
                    least = t
        return least

    @classmethod
    def mortgage_one(cls, player):

        if len(player.properties) > 0:
            to_mortgage = cls.least_valuable(player.properties)
            if to_mortgage is not None:
                return to_mortgage

        if len(player.stations) > 0:
            to_mortgage = cls.least_valuable(player.stations)
            if to_mortgage is not None:
                return to_mortgage

        if len(player.utilities) > 0:
            to_mortgage = cls.least_valuable(player.utilities)
            if to_mortgage is not None:
                return to_mortgage

