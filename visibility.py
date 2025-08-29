import math

"""
Idea:
we have "permanent" and "mobile" scanners.
Each player colony has a permanent scanner, which uses the star proximity hierarchy to reveal stars. 
Ships that are located at a star act as a "permanent scanner". 
Ships that are not located at a star act as mobile scanners, which do actively need to check their distance to 
different stars. 

Another idea:
A Scanner object locates objects within its radius, and marks them as "visible" to its "ruler". 
This is done by making a "visible" marking on the object. 
 - For now, Scanners can scan specifically for Ships and for Stars. 

A Visibility object simply consists of a list of bool, indexed by player. If the object is visible to the player, it
gets marked as True. This way, distances to scanners are checked at most once per tick. 

Another idea: an R-tree structure or similar, for "mobile scanners"
"""

class StarVisibility:

    def __init__(self, galaxy, player):
        # [star id][viewer id]
        self.galaxy = galaxy
        self.permanent_visible = [False for _ in range(len(galaxy.stars))]
        self.temporary_visible = [False for _ in range(len(galaxy.stars))]
        self.player = player

    def get_visible(self, star):
        return self.permanent_visible[star.id] or self.temporary_visible[star.id]

    def reset_permanent_visibility(self):
        self.permanent_visible = [False for _ in range(len(self.galaxy.stars))]
        visibility_range = self.player.technology.get_visibility_range()
        # Search through the player's ruled stars, and set the closest N stars as visible.
        for star in self.player.ruled_stars:
            self.permanent_visible[star.id] = True
            for j in self.galaxy.star_distance_hierarchy[star.id]:
                if self.galaxy.star_distance_matrix[star.id][j] < visibility_range:
                    self.permanent_visible[j] = True
                else:
                    break

    def set_temporary_visibility(self):
        """
        Sets temporary visibility.
        Avoids checking distances as much as possible, by avoiding:
         - checking stars that are permanently visible
         - checking ships that are at stars, and rather checking their distance hierarchy situation
        Also does not reset the list of bools, instead setting visibility to False if no longer visible in the "normal"
        way.
        """
        visibility_range = self.player.technology.get_visibility_range()
        for i in range(len(self.galaxy.stars)):
            visible = False
            if self.permanent_visible[i]:
                visible = True
            else:
                for ship in self.player.ships:
                    if ship.star is None:
                        if ship.get_distance_to(self.galaxy.stars[i].location) < visibility_range:
                            visible = True
                            break
            self.temporary_visible[i] = visible
        # Treat ships at stars as though this star is ruled
        for ship in self.player.ships:
            if ship.star is not None:
                self.temporary_visible[ship.star.id] = True
                for j in self.galaxy.star_distance_hierarchy[ship.star.id]:
                    if self.galaxy.star_distance_matrix[ship.star.id][j] < visibility_range:
                        self.temporary_visible[j] = True
                    else:
                        break

