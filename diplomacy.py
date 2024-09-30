

ACCESS_NAMES = "biomass diplomacy trade passage piracy battle siege".split()
# If an access type is hostile or not
# Hostile access types require the other player to exceed a certain negative leverage over the player
# Other access types can be granted and revoked, with an exchange of leverage
IS_HOSTILE = [False, False, False, False, True, True, True]
# The value, in leverage, of granting each type of access to another player,
# or of requiring that access from another player
# In the case of hostile access types, the value is the negative access required to take that action
ACCESS_LEVERAGE_VALUE = [35, 10, 10, 10, 10, 30, 50]
# The default access level at the game start
DEFAULT_ACCESS = [False, True, True, False, False, False, False]
REFLEXIVE_ACCESS = [True, True, True, True, False, False, False]

# The multiplier by which leverage is additionally lost for failing to repay a favour when asked
BETRAYAL_PENALTY = 2

class Diplomacy:

    def __init__(self, game):
        self.game = game
        # Matrix is ordered by: [i][j] gives leverage of player i over player j.
        self.leverage_matrix = [[0 for _ in range(len(game.players))] for _ in range(len(game.players))]
        # Which access types each player grants to each other
        # ordered by: [i][j][x] True means player j has access x in player i systems
        self.access_matrix = [[[DEFAULT_ACCESS[i] for i in range(len(ACCESS_NAMES))]
                               for _ in range(len(game.players))] for _ in range(len(game.players))]
        self.set_reflexive_access()

    def set_reflexive_access(self):
        """
        Ensures that "reflexive access", being access a player has in their own systems
        """
        for i in range(len(self.game.players)):
            for j in range(len(ACCESS_NAMES)):
                self.access_matrix[i][i][j] = REFLEXIVE_ACCESS[j]

    def get_negative_access(self, origin_id, dest_id):
        """
        Gets the 'negative access' amount for a player, the 'origin' player
        Negative access refers to the degree of negative leverage from the other player,
        for the purposes of justifying hostile actions against that player
        In effect, returns either the amount of negative leverage from the other player,
        or zero, if that player has positive (or zero) leverage over the origin
        """
        return -min(self.leverage_matrix[dest_id][origin_id], 0)

    def update_access(self):
        """
        Updates access that changes with leverage levels
        In particular, this means hostile access will change depending on the negative leverage level,
        and non-hostile access will be revoked if leverage is negative
        This method should be run whenever any player loses leverage
        in a situation where leverage might go below zero,
        or when a player gains leverage while having negative leverage
        """
        for origin in range(len(self.game.players)):
            for dest in range(len(self.game.players)):
                if origin != dest:
                    negative_access = self.get_negative_access(origin, dest)
                    for i in range(len(self.access_matrix[origin][dest])):
                        if IS_HOSTILE[i]:
                            self.access_matrix[origin][dest][i] = negative_access >= ACCESS_LEVERAGE_VALUE[i]
                        else:
                            self.access_matrix[origin][dest][i] = negative_access == 0

    def spend_leverage(self, origin_id, dest_id, amount):
        """
        Spends, or attempts to spend, an amount of leverage, meaning that the origin player has at least
        that much leverage available over the destination player
        Returns a boolean describing whether the operation was successful
        """
        if self.leverage_matrix[origin_id][dest_id] >= amount:
            self.leverage_matrix[origin_id][dest_id] -= amount
            return True
        return False

    def lose_leverage(self, origin_id, dest_id, amount):
        """
        Causes the origin player to lose leverage over the destination player, possibly into negative leverage
        If the origin player is in negative leverage, then access is updated as necessary
        """
        self.leverage_matrix[origin_id][dest_id] -= amount
        if self.leverage_matrix[origin_id][dest_id] < 0:
            self.update_access()

    def gain_leverage(self, origin_id, dest_id, amount):
        """
        Causes the origin player to gain leverage over the destination player
        If the origin player has negative leverage to begin with, then access is updated as necessary
        """
        old_leverage = self.leverage_matrix[origin_id][dest_id]
        self.leverage_matrix[origin_id][dest_id] += amount
        if old_leverage < 0:
            self.update_access()

    def get_milestone_state(self, player_id):
        total = 0
        for i in range(len(self.game.players)):
            total += self.leverage_matrix[i][player_id]
        return total / (len(self.game.players) - 1) / 100 * 2 * 1500
