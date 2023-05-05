import regex
import random
from shop import Shop
from items import Axe, Pickaxe
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from items import Tinderbox, Knife
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from items import CopperAxe, SteelAxe, MithrilAxe, AdamantAxe
from items import CopperOre, CoalOre, TinOre, IronOre, GoldOre
from items import OakLog, WillowLog, MapleLog, YewLog, MagicLog
from items import CopperPickaxe, SteelPickaxe, MithrilPickaxe, AdamantPickaxe
from items import OakShortbow, WillowShortbow, MagicShortbow, YewShortbow, MapleShortbow


class ShopTile(QLabel):
    # Abstract class, representing a tile on the game map that is an interface to a shop instance
    # There are different subtypes of shops, e.g. general shop or blacksmith shop, that have different initial stocks

    clicked = pyqtSignal(int, int)  # emit coordinates to interactable_clicked_on() on the Map object this tile is on

    def __init__(self, x, y, tile_width, tile_height, init_items, status_bar_signal):

        super().__init__()

        self.x, self.y = x, y
        self.setFixedSize(QSize(tile_width, tile_height))

        self.setPixmap(QPixmap(self.path_to_icon).scaled(self.size(), Qt.KeepAspectRatio))
        self.setAlignment(Qt.AlignCenter)

        self.shop = Shop(self.title, init_items, status_bar_signal)

    def mouseReleaseEvent(self, e):

        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.x, self.y)

        e.ignore()


class GeneralShop(ShopTile):
    # Concrete shop tile class representing a general shop

    title = 'General Shop'
    description = 'A general shop for buying and selling basic goods'
    path_to_icon = 'images/shop keeper.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):

        super().__init__(
            x=x, y=y, tile_width=tile_width, tile_height=tile_height,
            init_items=[CopperAxe() for i in range(2)] +
                       [CopperPickaxe() for i in range(2)] +
                       [Tinderbox() for i in range(3)] +
                       [Knife() for i in range(3)] +
                       [OakLog() for i in range(10)] +
                       [WillowLog() for i in range(5)],
            status_bar_signal=status_bar_signal
        )


class ArcheryShop(ShopTile):
    # Concrete shop tile class representing an archery shop

    title = 'Archery Shop'
    description = 'An archery shop for buying and selling goods related to archery'
    path_to_icon = 'images/archer.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):

        super().__init__(
            x=x, y=y, tile_width=tile_width, tile_height=tile_height,
            init_items=[OakShortbow() for i in range(5)] +
                       [WillowShortbow() for i in range(5)] +
                       [MapleShortbow() for i in range(3)] +
                       [YewShortbow() for i in range(2)] +
                       [MagicShortbow() for i in range(1)],
            status_bar_signal=status_bar_signal
        )


class BlacksmithShop(ShopTile):
    # Concrete shop tile class representing a blacksmith shop

    title = 'Blacksmith Shop'
    description = 'A blacksmith shop for buying and selling goods related to mining'
    path_to_icon = 'images/blacksmith.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):

        super().__init__(
            x=x, y=y, tile_width=tile_width, tile_height=tile_height,
            init_items=[CopperAxe() for i in range(5)] +
                       [SteelAxe() for i in range(5)] +
                       [MithrilAxe() for i in range(5)] +
                       [AdamantAxe() for i in range(3)] +
                       [CopperPickaxe() for i in range(5)] +
                       [SteelPickaxe() for i in range(5)] +
                       [MithrilPickaxe() for i in range(5)] +
                       [AdamantPickaxe() for i in range(3)],
            status_bar_signal=status_bar_signal
        )


class Tile(QLabel):
    # Abstract class for all non-empty tiles (except ShopTile above), having an image that to be displayed as an icon
    # `tile_width` and `tile_height` set the fixed size of the QLabel widget, that all tiles in the map share

    def __init__(self, x, y, tile_width, tile_height, scale_icon=None):
        # If we want to shrink the image a bit (within that fixed tile size), pass in a `scale_icon` > 1.0

        super().__init__()

        self.x, self.y = x, y
        self.setFixedSize(QSize(tile_width, tile_height))

        if scale_icon is not None:
            icon_size = QSize(int(tile_width/scale_icon), int(tile_height/scale_icon))
        else:
            icon_size = self.size()

        self.setPixmap(QPixmap(self.path_to_icon).scaled(icon_size, Qt.KeepAspectRatio))
        self.setAlignment(Qt.AlignCenter)


class EmptyTile(QLabel):
    # Empty tiles have no visual display

    def __init__(self, x, y, tile_width, tile_height):

        super().__init__()

        self.x, self.y = x, y
        self.setFixedSize(QSize(tile_width, tile_height))


class TransportTile(Tile):
    # An abstract tile class representing tiles which when clicked on transport the player
    # Every transport tile is written in the map json with:
    # - name to reference the concrete tile class,
    # - name of the map we are transporting
    # - coordinates of where on that map
    # e.g. 'CEntrance:cave:x:y', or 'LDown:lower_cave:x:y'
    # We can transport within the same map by setting the name of the map to the one we're already on, and whatever
    # coordinates are necessary
    # We can optionally specify requirements to use this transport tile, which are checked when clicked on
    # E.g. 'LDown:lower_cave:x:y:mining(5)' means we can only go down the ladder into the lower cave with >= 5 mining

    clicked = pyqtSignal(int, int)  # emit coordinates to interactable_clicked_on() on the Map object this tile is on

    def __init__(self, x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements):

        super().__init__(x, y, tile_width, tile_height)

        # str representing the name of the map this tile takes us to on clicking, e.g. 'cave' or 'lower_cave'
        self.destination = destination

        # coordinates of where on the transported map to land player
        self.destination_x = int(destination_x)
        self.destination_y = int(destination_y)

        # Parse the requirements string into a dictionary, mapping from specified skill string to the required level
        # Required format is space separated list of 'skill(number)'
        # E.g. 'mining(5)' or 'mining(5) woodcutting(10)'
        # will map to {'Mining': 5} or {'Mining': 5, 'Woodcutting': 10}
        self.requirements_string = requirements
        self.skill_requirements = {}
        skill_req_regex = regex.compile(r'^(\w+)\((\d{1,2})\)$')

        if requirements is not None:

            for skill_req in requirements.split(' '):

                skill_match = skill_req_regex.match(skill_req)
                self.skill_requirements[skill_match.group(1).title()] = int(skill_match.group(2))

    def mouseReleaseEvent(self, e):

        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.x, self.y)

        e.ignore()


class CaveEntrance(TransportTile):
    # Concrete transport tile representing a cave entrance

    title = 'Cave Entrance'
    description = 'Entrance to a cave'
    path_to_icon = 'images/cave entrance.jpg'

    def __init__(self, x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements):
        super().__init__(x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements)


class CaveExit(TransportTile):
    # Concrete transport tile representing a cave exit

    title = 'Cave Exit'
    description = 'Exit from a cave'
    path_to_icon = 'images/cave exit.jpg'

    def __init__(self, x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements):
        super().__init__(x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements)


class LadderDown(TransportTile):
    # Concrete transport tile representing a ladder down

    title = 'Ladder Down'
    description = 'Wonder what is down there?'
    path_to_icon = 'images/ladder_down.jpg'

    def __init__(self, x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements):
        super().__init__(x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements)


class LadderUp(TransportTile):
    # Concrete transport tile representing a ladder up

    title = 'Ladder Up'
    description = 'Wonder what is up there?'
    path_to_icon = 'images/ladder_up.jpg'

    def __init__(self, x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements):
        super().__init__(x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements)


class FireAltar(TransportTile):
    # Concrete transport tile representing a fire altar

    title = 'Fire Altar'
    description = 'For teleporting back to home!'
    path_to_icon = 'images/fire altar.jpg'

    def __init__(self, x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements):
        super().__init__(x, y, tile_width, tile_height, destination, destination_x, destination_y, requirements)


class BankChestTile(Tile):
    # A concrete tile class representing the interface to the shared game bank
    # When clicked on (when player within 1 tile), it will open the bank display widget in the game's main display

    clicked = pyqtSignal(int, int)  # emit coordinates to interactable_clicked_on() on the Map object this tile is on

    title = 'Bank Chest'
    description = 'Bank chest to interact with your bank'
    path_to_icon = 'images/bank chest.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)

    def mouseReleaseEvent(self, e):

        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.x, self.y)

        e.ignore()


class NPC(Tile):
    # Abstract tile class representing NPCs
    # Wanders a (2 x max radius + 1) x (2 x max radius + 1) grid, and moves every game tick
    # Only wanders onto empty tiles, not past map boundaries, and within it's max radius grid
    # If we set maximum radius large, we could have an NPC that moves over entire map - just set very large, doesn't
    # matter about map dimensions

    move = pyqtSignal(int, int)  # emit coordinates to npc_move() on the Map object this tile is on

    def __init__(self, x, y, tile_width, tile_height, scale_icon=None):

        super().__init__(x, y, tile_width, tile_height, scale_icon=scale_icon)

        # Can never move more than `self.maximum_radius` in either direction from these
        self.initial_x = x
        self.initial_y = y

        assert self.maximum_radius > 0

    def tick_move(self):
        # Slot for timer, move NPC every tick

        self.move.emit(self.x, self.y)


class Chicken(NPC):
    # Concrete NPC tile for a chicken

    title = 'Chicken'
    description = 'Good for feathers!'
    path_to_icon = 'images/chicken.jpg'
    maximum_radius = 2

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, scale_icon=2.5)


class Guard(NPC):
    # Concrete NPC tile for a guard

    title = 'Guard'
    description = "Don't pick a fight with him!"
    path_to_icon = 'images/guard.jpg'
    maximum_radius = 3

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class StrayDog(NPC):
    # Concrete NPC tile for a stray dog

    title = 'Stray Dog'
    description = 'Needs a loving home!'
    path_to_icon = 'images/stray dog.jpg'
    maximum_radius = 100  # Basically the entire map

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, scale_icon=1.5)


class Player(Tile):
    # Concrete tile for a player
    # There will only be one of these across all the maps in the game

    path_to_icon = 'images/player.jpg'

    def __init__(self, x, y, tile_width, tile_height):
        super().__init__(x, y, tile_width, tile_height)


class NonInteractable(Tile):
    # Abstract tile class for all non-interactable tiles, basically just scenery we or NPCs cannot move onto

    def __init__(self, x, y, tile_width, tile_height, scale_icon=None):
        super().__init__(x, y, tile_width, tile_height, scale_icon=scale_icon)


class TimedNonInteractable(NonInteractable):
    # Abstract class representing non-interactable tiles which should delete itself after a certain amount of game ticks
    # We should not put these in the map json files, rather dynamically create from the way player interacts with game,
    # e.g. a fire lit.
    # Therefore concrete classes subclassing this class are not in the dictionary mapping code to tile type
    # at the bottom of this file

    remove_signal = pyqtSignal(int, int)  # emits coordinates to map object this tile is on to handle removing

    def __init__(self, x, y, tile_width, tile_height, ticks_to_disappear, scale_icon=None):

        super().__init__(x, y, tile_width, tile_height, scale_icon=scale_icon)

        # `ticks_to_disappear` is how many game ticks should pass before we delete this tile from map
        self.ticks_left = ticks_to_disappear

    def count_down(self):
        # This function is emitted to every time game timer ticks

        assert self.ticks_left > 0

        self.ticks_left -= 1
        if self.ticks_left == 0:
            self.remove_signal.emit(self.x, self.y)


class Fire(TimedNonInteractable):
    # Concrete timed non-interactable class representing a fire
    # Created when using a tinderbox on logs in player's inventory
    # Different level logs create different Fire's with higher ticks to wait before they are removed

    title = 'Fire'
    description = 'Hot!'
    path_to_icon = 'images/fire.jpg'

    def __init__(self, x, y, tile_width, tile_height, ticks_for_fire_to_disappear):
        super().__init__(x, y, tile_width, tile_height, ticks_to_disappear=ticks_for_fire_to_disappear)


class WaterFountain(NonInteractable):
    # Concrete non-interactable tile representing water fountain scenery

    title = 'Water Fountain'
    description = 'Water fountain - if you are thirsty!'
    path_to_icon = 'images/water fountain.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class Cart(NonInteractable):
    # Concrete non-interactable tile representing cart scenery

    title = 'Cart'
    description = 'Needs its wheels fixing!'
    path_to_icon = 'images/cart.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class Anvil(NonInteractable):
    # Concrete non-interactable tile representing anvil scenery

    title = 'Anvil'
    description = 'For smithing items'
    path_to_icon = 'images/anvil.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class ArcheryBarrel(NonInteractable):
    # Concrete non-interactable tile representing archery barrel scenery

    title = 'Archery Barrel'
    description = 'For storing bows and arrows'
    path_to_icon = 'images/archery barrel.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class MiningBarrel(NonInteractable):
    # Concrete non-interactable tile representing mining barrel scenery

    title = 'Mining barrel'
    description = 'For storing pickaxes'
    path_to_icon = 'images/mining barrel.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class Crate(NonInteractable):
    # Concrete non-interactable tile representing crate scenery

    title = 'Crate'
    description = 'Wonder what is in here?'
    path_to_icon = 'images/crate.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, scale_icon=2)


class FurStall(NonInteractable):
    # Concrete non-interactable tile representing fur stall scenery

    title = 'Fur Stall'
    description = 'Stall selling fur items'
    path_to_icon = 'images/fur stall.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class BakeryStall(NonInteractable):
    # Concrete non-interactable tile representing bakery stall scenery

    title = 'Bakery Stall'
    description = 'Stall selling baked goods'
    path_to_icon = 'images/bakery stall.jpg'

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height)


class Interactable(Tile):
    # Abstract class representing something in the scenery we can interact with and deplete resources from
    # It is interacted with using a tool, and yields concrete resource items
    # Once all the resources have been depleted from it, it will take a certain amount of ticks to regenerate
    # Each time we interact with it, we have a probability of yielding the resources,
    # that depends on certain factors: relevant skill level, strength of tool, etc.
    # Will have multiple abstract subclasses for more specific items, e.g. Tree or Rock,
    # which in turn have subclasses that can be instantiated, e.g. Interactable -> Tree -> Oak Tree

    clicked = pyqtSignal(int, int)  # emit coordinates to interactable_clicked_on() on the Map object this tile is on

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal, scale_icon=None):

        super().__init__(x, y, tile_width, tile_height, scale_icon=scale_icon)

        self.status_bar_signal = status_bar_signal

        # How much `health` it has is how many resources it yields until it is depleted
        # It is a random number between the minimum and maximum bounds. Higher level trees/rocks have more health
        self.health = random.randint(self.minimum_health, self.maximum_health)

        if scale_icon is not None:
            icon_size = QSize(int(tile_width/scale_icon), int(tile_height/scale_icon))
        else:
            icon_size = self.size()

        # Load the two pixmaps for depleted and original image, to avoid creating new ones every time we swap states
        self.original_pixmap = QPixmap(self.path_to_icon).scaled(icon_size, Qt.KeepAspectRatio)
        self.depleted_pixmap = QPixmap(self.path_to_depleted_icon).scaled(icon_size, Qt.KeepAspectRatio)

        # The game timer emits to `regenerate()` every game tick
        # Every time we deplete, reset the number of game ticks we need to wait, `self.ticks_left`, to the amount
        self.ticks_left = None

    def deplete(self):
        # Change icon to a stump
        # Whenever we deplete, reset the ticks count to how many we need to wait for regeneration

        assert self.health == 0
        self.setPixmap(self.depleted_pixmap)
        self.ticks_left = self.ticks_to_regenerate

    def regenerate(self):
        # This slot is connected to the timer, and is called every game tick
        # If it's depleted and we are waiting to regenerate, count down how many ticks until regeneration
        # If tick count reached, regenerate: change icon to original icon, reset health, and tick counter

        if self.health == 0:

            self.ticks_left -= 1

            if self.ticks_left == 0:
                self.health = random.randint(self.minimum_health, self.maximum_health)
                self.setPixmap(self.original_pixmap)

    def interact(self, inventory, skills):
        # Takes a player's inventory, so we can:
        # - get the best tool we have in the inventory
        # - make sure we don't deplete more than we have space for
        # - add the yielded items to it after interaction.
        # Also takes player's skill levels to:
        # - check we get the best tool in the inventory we actually have the skill level to use
        # - add xp to the relevant skill after interaction.

        # Check we can interact: i.e. it's not depleted, and we have space in inventory

        assert self.health > 0

        if inventory.is_full():
            # No space in inventory to receive yielded items
            self.status_bar_signal.emit("Inventory full - cannot receive more items")
            return

        # Get the tool from our inventory we will use in this interaction

        # `get_tool` gets best tool in inventory (i.e. one with highest strength) that we can use based on our skills
        tool = inventory.get_tool(
            tool_type=self.tool_type_required,
            skill_set=skills
        )

        if tool is None or tool.strength < self.minimum_tool_required.strength:
            # No tool in inventory of type needed for interaction (or at least one we can use based on skills)
            # that is at least strong enough
            self.status_bar_signal.emit(
                "No tool available for interaction! "
                "Check your inventory and that you have the required skill level for the right strength tool"
            )
            return

        # Every time we interact with the tree/rock we have a chance of taking one log/ore
        # The success rate depends on the type of tool used, our skill level, and the tree/rock interacting with
        # For each tree/rock, picture a graph of success rate vs. woodcutting/mining level, and a line for each tool,
        # with higher strength tools having higher intercepts (and same gradient)
        # Analogous tree and rocks share the same success rate,
        # e.g. oak tree + steel axe + wc level <=> copper/tin rock + steel pick + mining level
        # e.g. magic tree + addy axe + wc level <=> gold rock + addy pick + mining level

        # Returns a probability between 0 and 1, and randomly decide if we should deplete, proportional to probability
        # `self.success_rate` needs to be implemented in each subclass (i.e. for each specific tree/rock)
        probability = self.success_rate(skill=skills.relevant_skill(tool), tool=tool)
        to_deplete = random.random() < probability

        # Do the damage depletion if we succeeded this interaction
        if to_deplete:

            self.health -= 1

            item = self.resource_type_yielded()

            # Xp is gained by two different mechanics: generation and processing
            # Here we have generated items, so we gain the xp in the relevant skill for generation
            # (logs in woodcutting, ores in mining)
            skills.add_experience([item], generated=True)
            inventory.add_to([item])

            # If tree is now depleted, set to depleted and the game timer will tick until it regenerates
            # It is no longer able to be interacted with until it's regenerated
            if self.health == 0:
                self.deplete()

        else:
            self.status_bar_signal.emit("You missed!")

    def mouseReleaseEvent(self, e):
        # Only interact with the tile on a left-click if it is not depleted

        if e.button() == Qt.LeftButton:

            if self.health > 0:
                self.clicked.emit(self.x, self.y)
            else:
                self.status_bar_signal.emit("Wait for it to regenerate!")

        e.ignore()


class Tree(Interactable):
    # Abstract class to represent all trees
    # Interacted with using an axe
    # Different tree subclasses require higher strength axes, yield higher level logs, and have higher health levels

    tool_type_required = Axe

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal)
        assert issubclass(self.minimum_tool_required, self.tool_type_required)


class OakTree(Tree):
    # Concrete tree tile representing oak trees, that yield oak logs

    title = 'Oak Tree'
    description = 'An oak tree that yields oak logs on chopping with a copper axe or better'
    resource_type_yielded = OakLog
    minimum_tool_required = CopperAxe
    path_to_icon = 'images/oak tree.jpg'
    path_to_depleted_icon = 'images/tree stump.jpg'
    minimum_health = 3
    maximum_health = 5
    ticks_to_regenerate = 10

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):
        # Success rate depends on three things:
        # - the type of tree. Higher level trees have lower success rates for the same skill level & axe type
        # - woodcutting level: higher woodcutting level means higher success rate
        # - tool type: higher level tools have higher success rates
        # Our skill level is guaranteed to be high enough to use the tool,
        # and the tool is guaranteed to be able to be used on this tree
        # We only need to consider the tool types above the minimum tool type
        # Each tool type has a y=mx+c line. All tool types have same gradient, but higher tools have higher intercepts

        gradient = 25/9

        if isinstance(tool, CopperAxe):
            intercept = 200/9
        elif isinstance(tool, SteelAxe):
            intercept = 325/9
        elif isinstance(tool, MithrilAxe):
            intercept = 470/9
        else:
            assert isinstance(tool, AdamantAxe)
            intercept = 555/9

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class WillowTree(Tree):
    # Concrete tree tile representing willow trees, that yield willow logs

    title = 'Willow Tree'
    description = 'A willow tree that yields willow logs on chopping with a steel axe or better'
    resource_type_yielded = WillowLog
    minimum_tool_required = SteelAxe
    path_to_icon = 'images/willow tree.jpg'
    path_to_depleted_icon = 'images/tree stump.jpg'
    minimum_health = 6
    maximum_health = 10
    ticks_to_regenerate = 20

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 4

        if isinstance(tool, SteelAxe):
            intercept = 10
        elif isinstance(tool, MithrilAxe):
            intercept = 20
        else:
            assert isinstance(tool, AdamantAxe)
            intercept = 27

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class MapleTree(Tree):
    # Concrete tree tile representing maple trees, that yield maple logs

    title = 'Maple Tree'
    description = 'A maple tree that yields maple logs on chopping with a mithril axe or better'
    resource_type_yielded = MapleLog
    minimum_tool_required = MithrilAxe
    path_to_icon = 'images/maple tree.jpg'
    path_to_depleted_icon = 'images/tree stump.jpg'
    minimum_health = 10
    maximum_health = 15
    ticks_to_regenerate = 30

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 3

        if isinstance(tool, MithrilAxe):
            intercept = 20
        else:
            assert isinstance(tool, AdamantAxe)
            intercept = 29

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class YewTree(Tree):
    # Concrete tree tile representing yew trees, that yield yew logs

    title = 'Yew Tree'
    description = 'A yew tree that yields yew logs on chopping with a mithril axe or better'
    resource_type_yielded = YewLog
    minimum_tool_required = MithrilAxe
    path_to_icon = 'images/yew tree.jpg'
    path_to_depleted_icon = 'images/tree stump.jpg'
    minimum_health = 15
    maximum_health = 20
    ticks_to_regenerate = 45

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 3

        if isinstance(tool, MithrilAxe):
            intercept = 10
        else:
            assert isinstance(tool, AdamantAxe)
            intercept = 19

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class MagicTree(Tree):
    # Concrete tree tile representing magic trees, that yield magic logs

    title = 'Magic Tree'
    description = 'A magic tree that yields magic logs on chopping with a addamant axe or better'
    resource_type_yielded = MagicLog
    minimum_tool_required = AdamantAxe
    path_to_icon = 'images/magic tree.jpg'
    path_to_depleted_icon = 'images/tree stump.jpg'
    minimum_health = 15
    maximum_health = 25
    ticks_to_regenerate = 60

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 2.5

        assert isinstance(tool, AdamantAxe)
        intercept = 15

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class Rock(Interactable):
    # Abstract class to represent all rocks
    # Interacted with using a pickaxe
    # Different rock subclasses require higher strength pickaxes, yield higher level ores, and have higher health levels

    tool_type_required = Pickaxe

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal, scale_icon=1.5)
        assert issubclass(self.minimum_tool_required, self.tool_type_required)


class CopperRock(Rock):
    # Concrete rock tile representing copper rocks, that yield copper ores

    title = 'Copper Rock'
    description = 'A copper rock that yields copper ores on mining with a copper pickaxe or better'
    resource_type_yielded = CopperOre
    minimum_tool_required = CopperPickaxe
    path_to_icon = 'images/copper rock.jpg'
    path_to_depleted_icon = 'images/empty rock.jpg'
    minimum_health = 3
    maximum_health = 5
    ticks_to_regenerate = 10

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):
        # Success rate depends on three things:
        # - the type of rock. Higher level rocks have lower success rates for the same skill level & pickaxe type
        # - mining level: higher mining level means higher success rate
        # - tool type: higher level tools have higher success rates
        # Our skill level is guaranteed to be high enough to use the tool,
        # and the tool is guaranteed to be able to be used on this rock
        # We only need to consider the tool types above the minimum tool type
        # Each tool type has a y=mx+c line. All tool types have same gradient, but higher tools have higher intercepts

        gradient = 25/9

        if isinstance(tool, CopperPickaxe):
            intercept = 200/9
        elif isinstance(tool, SteelPickaxe):
            intercept = 325/9
        elif isinstance(tool, MithrilPickaxe):
            intercept = 470/9
        else:
            assert isinstance(tool, AdamantPickaxe)
            intercept = 555/9

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class TinRock(Rock):
    # Concrete rock tile representing tin rocks, that yield tin ores

    title = 'Tin Rock'
    description = 'A tin rock that yields tin ores on mining with a copper pickaxe or better'
    resource_type_yielded = TinOre
    minimum_tool_required = CopperPickaxe
    path_to_icon = 'images/tin rock.jpg'
    path_to_depleted_icon = 'images/empty rock.jpg'
    minimum_health = 3
    maximum_health = 5
    ticks_to_regenerate = 10

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 25/9

        if isinstance(tool, CopperPickaxe):
            intercept = 200/9
        elif isinstance(tool, SteelPickaxe):
            intercept = 325/9
        elif isinstance(tool, MithrilPickaxe):
            intercept = 470/9
        else:
            assert isinstance(tool, AdamantPickaxe)
            intercept = 555/9

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class CoalRock(Rock):
    # Concrete rock tile representing coal rocks, that yield coal ores

    title = 'Coal Rock'
    description = 'A coal rock that yields coal ores on mining with a steel pickaxe or better'
    resource_type_yielded = CoalOre
    minimum_tool_required = SteelPickaxe
    path_to_icon = 'images/coal rock.jpg'
    path_to_depleted_icon = 'images/empty rock.jpg'
    minimum_health = 6
    maximum_health = 10
    ticks_to_regenerate = 20

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 4

        if isinstance(tool, SteelPickaxe):
            intercept = 10
        elif isinstance(tool, MithrilPickaxe):
            intercept = 20
        else:
            assert isinstance(tool, AdamantPickaxe)
            intercept = 27

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class IronRock(Rock):
    # Concrete rock tile representing iron rocks, that yield iron ores

    title = 'Iron Rock'
    description = 'An iron rock that yields iron ores on mining with a mithril pickaxe or better'
    resource_type_yielded = IronOre
    minimum_tool_required = MithrilPickaxe
    path_to_icon = 'images/iron rock.jpg'
    path_to_depleted_icon = 'images/empty rock.jpg'
    minimum_health = 10
    maximum_health = 15
    ticks_to_regenerate = 30

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 3

        if isinstance(tool, MithrilPickaxe):
            intercept = 20
        else:
            assert isinstance(tool, AdamantPickaxe)
            intercept = 29

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


class GoldRock(Rock):
    # Concrete rock tile representing gold rocks, that yield gold ores

    title = 'Gold Rock'
    description = 'A gold rock that yields gold ores on mining with a adamant pickaxe or better'
    resource_type_yielded = GoldOre
    minimum_tool_required = AdamantPickaxe
    path_to_icon = 'images/gold rock.jpg'
    path_to_depleted_icon = 'images/empty rock.jpg'
    minimum_health = 10
    maximum_health = 20
    ticks_to_regenerate = 60

    def __init__(self, x, y, tile_width, tile_height, status_bar_signal):
        super().__init__(x, y, tile_width, tile_height, status_bar_signal=status_bar_signal)

    def success_rate(self, skill, tool):

        gradient = 2.5

        assert isinstance(tool, AdamantPickaxe)
        intercept = 15

        x = skill.level

        assert x >= tool.skill_level_required

        y = (gradient * x) + intercept
        y /= 100

        if y > 1.0:
            y = 1.0

        return y


# We define a letter code to represent each concrete tile type that can be instantiated
# We use these codes to manually draw the game maps in the JSON files
code_to_feature = {
    # Trees
    'OT': OakTree,
    'WT': WillowTree,
    'MT': MapleTree,
    'YT': YewTree,
    'MagicT': MagicTree,
    # Rocks
    'CR': CopperRock,
    'TR': TinRock,
    'C': CoalRock,
    'IR': IronRock,
    'GR': GoldRock,
    # Shops
    'GS': GeneralShop,
    'BS': BlacksmithShop,
    'AS': ArcheryShop,
    # Banks
    'BC': BankChestTile,
    # Non-interactables
    'WF': WaterFountain,
    'Cart': Cart,
    'Anvil': Anvil,
    'ABarrel': ArcheryBarrel,
    'MBarrel': MiningBarrel,
    'Crate': Crate,
    'FStall': FurStall,
    'BStall': BakeryStall,
    # NPCs
    'Chicken': Chicken,
    'Dog': StrayDog,
    'Guard': Guard,
    # Transport Tiles
    'CEntrance': CaveEntrance,
    'CExit': CaveExit,
    'LDown': LadderDown,
    'LUP': LadderUp,
    'FAltar': FireAltar
}
