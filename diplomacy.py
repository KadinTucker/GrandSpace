

ACTIVE_ACCESS_NAMES = "biomass diplomacy trade passage".split()
HOSTILE_ACCESS_NAMES = "defence piracy battle siege".split()
# The value, in leverage, of granting each type of access to another player,
# or of requiring that access from another player
# In the case of hostile access types, the value is the negative access required to take that action
ACCESS_LEVERAGE_VALUE = [35, 10, 10, 10]
HOSTILE_LEVERAGE_THRESHOLD = [0, -10, -30, -50]
# The default access level at the game start
DEFAULT_ACCESS = [False, True, True, True]
REFLEXIVE_ACCESS = [True, True, True, True]

# The multiplier by which leverage is additionally lost for failing to repay a favour when asked
BETRAYAL_PENALTY = 2

class Diplomacy:

    def __init__(self, game):
        self.game = game
        # Matrix is ordered by: [i][j] gives leverage of player i over player j.
        self.leverage_matrix = [[0 for _ in range(len(game.players))] for _ in range(len(game.players))]
        # Which active and hostile, respectively, access types each player grants to each other
        # ordered by: [i][j][x] True means player j has access x in player i systems
        self.active_access_matrix = [[[DEFAULT_ACCESS[i] for i in range(len(ACTIVE_ACCESS_NAMES))]
                                     for _ in range(len(game.players))] for _ in range(len(game.players))]
        self.hostile_access_matrix = [[[False for i in range(len(HOSTILE_ACCESS_NAMES))]
                                      for _ in range(len(game.players))] for _ in range(len(game.players))]
        # For each player i, [i][j] is the total leverage they have gained over player j
        self.total_leverage_matrix = [[0 for _ in range(len(game.players))] for _ in range(len(game.players))]
        self.set_reflexive_access()

    def set_reflexive_access(self):
        """
        Ensures that "reflexive access", being access a player has in their own systems,
        is set.
        """
        for i in range(len(self.game.players)):
            for j in range(len(ACTIVE_ACCESS_NAMES)):
                self.active_access_matrix[i][i][j] = REFLEXIVE_ACCESS[j]

    def revoke_access(self, origin_id, dest_id, access_id):
        """
        If some active access is granted, revoke it.
        """
        if self.active_access_matrix[origin_id][dest_id][access_id]:
            self.active_access_matrix[origin_id][dest_id][access_id] = False
            self.lose_leverage(origin_id, dest_id, ACCESS_LEVERAGE_VALUE[access_id])

    def offer_access(self, origin_id, dest_id, access_id):
        if not self.active_access_matrix[origin_id][dest_id][access_id]:
            self.active_access_matrix[origin_id][dest_id][access_id] = True
            self.gain_leverage(origin_id, dest_id, ACCESS_LEVERAGE_VALUE[access_id])

    def get_negative_access(self, origin_id, dest_id):
        """
        Gets the 'negative access' amount for a player, the 'origin' player
        Negative access refers to the degree of negative leverage from the other player,
        for the purposes of justifying hostile actions against that player
        In effect, returns either the amount of negative leverage from the other player,
        or zero, if that player has positive (or zero) leverage over the origin
        """
        return -min(self.leverage_matrix[dest_id][origin_id], 0)

    def get_active_access(self, origin_id, dest_id, access_id):
        """
        Returns whether the origin_id player grants access_id access (active) to dest_id.
        If dest_id has negative relations with origin_id, all access is temporarily blocked.
        """
        return (self.leverage_matrix[dest_id][origin_id] >= 0
                and self.active_access_matrix[origin_id][dest_id][access_id])

    def get_hostile_access(self, origin_id, dest_id, access_id):
        return self.hostile_access_matrix[origin_id][dest_id][access_id]

    def update_hostile_access(self):
        """
        Updates access that passively changes with leverage levels
        In particular, this means hostile access will change depending on the negative leverage level,
        and non-hostile access will be revoked if leverage is negative
        This method should be run whenever any player loses leverage
        in a situation where leverage might go below zero,
        or when a player gains leverage while having negative leverage
        """
        for origin in range(len(self.game.players)):
            for dest in range(len(self.game.players)):
                if origin != dest:
                    for i in range(len(self.hostile_access_matrix[origin][dest])):
                        self.hostile_access_matrix[dest][origin][i] = (self.leverage_matrix[dest][origin]
                                                                       <= HOSTILE_LEVERAGE_THRESHOLD[i])

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
        self.total_leverage_matrix[origin_id][dest_id] -= amount
        self.leverage_matrix[origin_id][dest_id] = max(-100, self.leverage_matrix[origin_id][dest_id])
        self.update_hostile_access()

    def gain_leverage(self, origin_id, dest_id, amount):
        """
        Causes the origin player to gain leverage over the destination player
        If the origin player has negative leverage to begin with, then access is updated as necessary
        """
        self.leverage_matrix[origin_id][dest_id] += amount
        self.total_leverage_matrix[origin_id][dest_id] += amount
        self.leverage_matrix[origin_id][dest_id] = min(100, self.leverage_matrix[origin_id][dest_id])
        self.update_hostile_access()

    def get_milestone_state(self, player_id):
        """
        Gets the milestone state of a player:
        the amount of leverage gained more over each player than each player has gained over the player
        (i.e., infinite cycling does not work)
        Negative amounts do not count against one's milestone score
        """
        total = 0
        for i in range(len(self.game.players)):
            total += 10 * max(self.total_leverage_matrix[player_id][i] - self.total_leverage_matrix[i][player_id], 0)
        return total / (len(self.game.players) - 1)
