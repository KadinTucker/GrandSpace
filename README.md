# Grand Space

A grand(-ish) space strategy game inspired by various space opera/sci-fi games programmed with Python and pygame.

## Running the game

The game is programmed using the pygame library for Python, which is available, e.g. through the `pip` package manager for Python. Check out `pygame.org` for more details.

Python version 3 is best, though I think it should be compatible with Python 2. 

Run the command `python display.py`, and all else being well with your Python/pygame installation, it should work. 

## Why Python

I started this project in December 2023, though I had the idea for it further back. I decided to use Python and pygame after the amateur programmer that is me did not want to wrestle with unfamiliar graphics libraries and deal with programming languages I don't fully understand. Doing it in pygame means I can actually make something resembling progress. 

# The Game

You control a spacefaring empire that has just learned the secrets of interstellar travel. However, you are not the only ones to do so. 

The Galaxy consists of several star systems, each with 1-5 planets. Planets can be colonized and have their minerals harvested and sold to other colonies, allowing for upgrades to your ships, colonies, and more. 

The amount that you can do as a player is limited by how much money you have and how many ships you have. 

## Overview of Game Mechanics

### Colonies

Each player starts with a homeworld colony, which, after centuries of overharvesting and pollution during its primitive phases of technological development, is no longer very productive. The player should instead expand out into the wider galaxy and establish colonies on other planets. 

Colonies have two levels of development: 
- Number of cities: the number of cities determines the maximum development and the maximum storage capacity of minerals
- Development: capped by the number of cities as well as the habitability of the planet (see more later), determines how quickly minerals are produced

Planets have varying levels of habitability, which determines how much the planet can be developed. Habitability is discussed in more depth with terraforming. 

### Exploration

Throughout the galaxy are scattered mysterious alien artifacts that contain long-lost secrets and treasures that can be used to kick-start a player's empire. Without these artifacts, investing in colonies will be very difficult. 

Artifacts are located in random places around the galaxy, and ships are needed to go looking for them. Collecting artifacts and returning them to the homeworld gives a small amount of money. 

### Science

Science allows for upgrading technology, including ship equipment, colony development, and just about everything. 

Science comes in three flavors:
- Power: combat and war, settlement and expansion
- Harmony: diplomacy and ecology
- Prosperity: trade, mineral production, ships

Technologies have costs in particular flavors (i.e., power technologies, harmony technologies, prosperity technologies). Science can be converted to different flavors at a cost. 

Science is earned in three ways:
- Milestones: there are six milestone categories, and when certain objectives are achieved, a boost to science is provided, with some flavored and some wild
- Research Missions: ships can "trade" for science, granting a small amount of wild science and some money
- Consumption: each flavor of science can be produced additionally through certain costs

The milestone categories are:
- Exploration: gained through exploring new stars and collecting artifacts; grants prosperity science
- Wealth: gained through earning and having money; grants prosperity science
- Military: gained through combat, conquest, and defense; grants power science
- Empire: gained through expansion, settlement, and development; grants power science
- Ecology: gained through collecting biomass and terraforming; grants harmony science
- Diplomacy: gained through making allies and doing diplomatic actions; grants harmony science

Consumption sources are:
- Paying money to gain prosperity science
- Consuming biomass to gain harmony science
- Participating in battles to gain power science, especially as the defender

### Trade

Colonies, once sufficiently developed, produce minerals, which other colonies will buy. The amount each colony will pay for the mineral varies sporadically, so trading partners should change occasionally for the best value. Ships need to carry the minerals between planets, which takes time. 

Colonies have a number, based on the number of cities, of minerals currently demanded. Of these, they have a demand which can be between 1 and 5, and determines the price they will pay for the mineral. The demand for the mineral will eventually fade away and a new mineral will be demanded. Minerals that are not demanded can still be sold, but at a very low price.

Ships can have a variety of trade methods, and more unlocked with propserity technology. Having a low supply of minerals will mean that the best method is to search and wait for the best possible price. Having a high supply of minerals means the ship is rather time-limited than mineral-limited, and so will settle for lower prices. 

### Diplomacy

Players can interact with each other by doing favors for each other and earning leverage points. Doing a favor for another player grants leverage points over that player. One player sufficient leverage on another player means that they can ask for certain favors, including money, military support, or enforcing peace.

Players with neutral relations have no limits on what happens between them. Players can act hostile to others by not allowing them passage through their systems (firing upon them if they do), not allowing buying and/or selling of minerals, or conducting piracy. If relations sufficiently deteriorate, the players can end up in open war, fighting battles over planets and territories. 

### Warfare

Players' ships may likely end up in conflict, whether for conquest of planets, expand mercantile influence, or hold back winning players from steamrolling the game. 

Hostile ships within the same star system will fire long-distance weapons at each other, inflicting limited damage. Hostile ships at the same planet as one another will be in open combat, dealing more damage to each other. Ships on planets may also be trying to plunder the planet's mineral stores or be trying to take over the planet's cities, in which case they will not be fighting back. 

Conquest has its limits and causes the other player to gain leverage. With enough leverage, the other player may be able to enforce peace. 

### Terraforming

A final, wildcard aspect of the game is terraforming, which vastly improves colonies by increasing the planet's habitability. Terraforming requires biomass as a base component, which then, at the cost of a lot of money and ship time, can be used to boost the ecosystem of a planet. 

Biomass can be collected from planets with habitability, including players' homeworlds, but also including some planets throughout the galaxy. Biomass needs to come from a few different sources to have enough biodiversity for the destination planet. 

Biomass can be consumed and converted into harmony science. 