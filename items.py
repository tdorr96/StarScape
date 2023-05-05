class Item:
    # Base abstract class for all items: tools, weapons, resources, etc.

    def __init__(self):
        super().__init__()

    def __str__(self):
        return self.title


class Weapon(Item):
    # Abstract class for all weapon items

    def __init__(self):
        super().__init__()


class Bow(Weapon):
    # Abstract class for all bow items

    def __init__(self):
        super().__init__()


class OakShortbow(Bow):
    # Concrete item representing an Oak Shortbow

    title = 'Oak Shortbow'
    description = 'Shortbow made from an oak log for firing arrows'
    path_to_icon = 'images/oak shortbow.jpg'
    sell_price = 30
    buy_price = 150

    def __init__(self):
        super().__init__()


class WillowShortbow(Bow):
    # Concrete item representing a Willow Shortbow

    title = 'Willow Shortbow'
    description = 'Shortbow made from a willow log for firing arrows'
    path_to_icon = 'images/willow shortbow.jpg'
    sell_price = 50
    buy_price = 200

    def __init__(self):
        super().__init__()


class MapleShortbow(Bow):
    # Concrete item representing a Maple Shortbow

    title = 'Maple Shortbow'
    description = 'Shortbow made from a maple log for firing arrows'
    path_to_icon = 'images/maple shortbow.jpg'
    sell_price = 100
    buy_price = 400

    def __init__(self):
        super().__init__()


class YewShortbow(Bow):
    # Concrete item representing a Yew Shortbow

    title = 'Yew Shortbow'
    description = 'Shortbow made from a yew log for firing arrows'
    path_to_icon = 'images/yew shortbow.jpg'
    sell_price = 125
    buy_price = 600

    def __init__(self):
        super().__init__()


class MagicShortbow(Bow):
    # Concrete item representing a Magic Shortbow

    title = 'Magic Shortbow'
    description = 'Shortbow made from a magic log for firing arrows'
    path_to_icon = 'images/magic shortbow.jpg'
    sell_price = 200
    buy_price = 1000

    def __init__(self):
        super().__init__()


class Resource(Item):
    # Abstract class for all resource items. Will have multiple abstract subclasses for more specific resources,
    # e.g. Log or Ore, which in turn have subclasses that can be instantiated, e.g. Resource -> Log -> Oak Log

    def __init__(self):
        super().__init__()


class Log(Resource):
    # Abstract class to be subclassed by all instantiable Log types, e.g. Oak Logs, Willow Logs, etc.

    def __init__(self):
        super().__init__()


class OakLog(Log):
    # Concrete log item for an Oak Log

    title = 'Oak Log'
    description = 'Oak log obtained from chopping an oak tree with an axe'
    path_to_icon = 'images/oak log.jpg'
    sell_price = 10
    buy_price = 50
    fletching_required = 1
    firemaking_required = 1
    ticks_for_fire_to_disappear = 10

    def __init__(self):
        super().__init__()


class WillowLog(Log):
    # Concrete log item for a Willow Log

    title = 'Willow Log'
    description = 'Willow log obtained from chopping a willow tree with an axe'
    path_to_icon = 'images/willow log.jpg'
    sell_price = 30
    buy_price = 100
    fletching_required = 4
    firemaking_required = 5
    ticks_for_fire_to_disappear = 15

    def __init__(self):
        super().__init__()


class MapleLog(Log):
    # Concrete log item for a Maple Log

    title = 'Maple Log'
    description = 'Maple log obtained from chopping a maple tree with an axe'
    path_to_icon = 'images/maple log.jpg'
    sell_price = 50
    buy_price = 150
    fletching_required = 6
    firemaking_required = 8
    ticks_for_fire_to_disappear = 20

    def __init__(self):
        super().__init__()


class YewLog(Log):
    # Concrete log item for an Yew Log

    title = 'Yew Log'
    description = 'Yew log obtained from chopping a yew tree with an axe'
    path_to_icon = 'images/yew log.jpg'
    sell_price = 75
    buy_price = 200
    fletching_required = 8
    firemaking_required = 10
    ticks_for_fire_to_disappear = 30

    def __init__(self):
        super().__init__()


class MagicLog(Log):
    # Concrete log item for a Magic Log

    title = 'Magic Log'
    description = 'Magic Log obtained from chopping a magic tree with an axe'
    path_to_icon = 'images/magic log.jpg'
    sell_price = 100
    buy_price = 500
    fletching_required = 12
    firemaking_required = 12
    ticks_for_fire_to_disappear = 60

    def __init__(self):
        super().__init__()


class Ore(Resource):
    # Abstract class to be subclassed by all instantiable Ore types, e.g. Copper Ore, Coal Ore, etc.

    def __init__(self):
        super().__init__()


class CopperOre(Ore):
    # Concrete ore item for Copper Ore

    title = 'Copper Ore'
    description = 'Copper ore obtained from mining a copper ore rock with a pickaxe'
    path_to_icon = 'images/copper ore.jpg'
    sell_price = 15
    buy_price = 30

    def __init__(self):
        super().__init__()


class TinOre(Ore):
    # Concrete ore item for Tin Ore

    title = 'Tin Ore'
    description = 'Tin ore obtained from mining a tin ore rock using a pickaxe'
    path_to_icon = 'images/tin ore.jpg'
    sell_price = 15
    buy_price = 30

    def __init__(self):
        super().__init__()


class CoalOre(Ore):
    # Concrete ore item for Coal Ore

    title = 'Coal Ore'
    description = 'Coal ore obtained from mining a coal rock using a pickaxe'
    path_to_icon = 'images/coal ore.jpg'
    sell_price = 30
    buy_price = 75

    def __init__(self):
        super().__init__()


class IronOre(Ore):
    # Concrete ore item for Iron Ore

    title = 'Iron Ore'
    description = 'Iron ore obtained from mining an iron ore rock using a pickaxe'
    path_to_icon = 'images/iron ore.jpg'
    sell_price = 60
    buy_price = 150

    def __init__(self):
        super().__init__()


class GoldOre(Ore):
    # Concrete ore item for Gold Ore

    title = 'Gold Ore'
    description = 'Gold ore obtained from mining a gold rock using a pickaxe'
    path_to_icon = 'images/gold ore.jpg'
    sell_price = 60
    buy_price = 100

    def __init__(self):
        super().__init__()


class Tool(Item):
    # Abstract class for tool items. Will have multiple abstract subclasses for more specific tools, e.g. Axe

    def __init__(self):
        super().__init__()

    def use_on_resource_item(self, skills, resource, visible_map):
        # If we use a tool on a resource (or vica-versa) in the inventory, we want to try and combine them
        # Obviously not all combinations make sense (e.g. tinderbox on an ore?!), so most of the combinations won't
        # do anything. This is the purpose of this function.
        # If we overwrite this function in a subclass, we will handle the interaction there,
        # otherwise assume the tool cannot be used on a resource and fails to combine

        return {
            'success': False,
            'message': "You don't know how to use this tool on any resource"
        }


class Tinderbox(Tool):
    # Concrete tool item for Tinderbox

    title = 'Tinderbox'
    description = 'Tinderbox for lighting logs'
    path_to_icon = 'images/tinderbox.jpg'
    skill_level_required = 1  # We can always use a tinderbox, we never really check if >= 1 firemaking
    sell_price = 10
    buy_price = 100

    def __init__(self):
        super().__init__()

    def use_on_resource_item(self, skills, resource, visible_map):

        # Check we're trying to use the tinderbox on a log
        if not isinstance(resource, Log):
            return {
                'success': False,
                'message': "You can only use a tinderbox on a log"
            }

        # Check we have the skill level to use this tinderbox (redundant, as it's 1 but good practice to check)
        if not skills.can_use(self):
            return {
                'success': False,
                'message': "You don't have the skill level to use this tinderbox"
            }

        # Check we have the skill level to burn this log type
        if not skills.can_burn(resource):
            return {
                'success': False,
                'message': "You don't have the skill level to burn this log"
            }

        # Check we can light a log on the map
        if not visible_map.can_light_fire():
            return {
                'success': False,
                'message': "You cannot light a fire here"
            }

        # We can do the processing, i.e. burning the log and gaining firemaking xp
        # We are processing item, which has a different skill mapping than generation (e.g. generating logs from tree)
        # processing a log is firemaking xp, generating a log is woodcutting xp
        skills.add_experience([resource], generated=False)
        visible_map.light_fire(resource.ticks_for_fire_to_disappear)

        return {
            'success': True,
            'action': 'remove'
        }


class Knife(Tool):
    # Concrete tool item for Knife

    title = 'Knife'
    description = 'Knife for shaping logs into items like bows'
    path_to_icon = 'images/knife.jpg'
    skill_level_required = 1  # we can always use a knife, we never really check if >= 1 fletching
    sell_price = 10
    buy_price = 75

    def __init__(self):
        super().__init__()

    def use_on_resource_item(self, skills, resource, visible_map):

        # Check we're trying to use a knife on a log
        if not isinstance(resource, Log):
            return {
                'success': False,
                'message': "You can only use a knife on a log"
            }

        # Check we have the skill level to use this knife (redundant, as it's 1 but good practice to check)
        if not skills.can_use(self):
            return {
                'success': False,
                'message': "You don't have the skill level to use this knife"
            }

        # Check we have the skill level to fletch this log type
        if not skills.can_fletch(resource):
            return {
                'success': False,
                'message': "You don't have the skill level to fletch this log"
            }

        # We can do the processing, i.e. turning the log into a shortbow of corresponding type
        # We are generating an item, a shortbow, so make sure to use generation xp mapping

        generated_item = {
            OakLog: OakShortbow,
            WillowLog: WillowShortbow,
            MapleLog: MapleShortbow,
            YewLog: YewShortbow,
            MagicLog: MagicShortbow
        }[type(resource)]()

        skills.add_experience([generated_item], generated=True)

        return {
            'success': True,
            'action': 'replace',
            'generated_item': generated_item
        }


class Axe(Tool):
    # Abstract class to be subclassed by all instantiable woodcutting axe types, e.g. Copper Axe, Steel Axe, etc.

    def __init__(self):
        super().__init__()


class CopperAxe(Axe):
    # Concrete axe item for Copper Axe

    title = 'Copper Axe'
    description = 'Copper Axe for chopping down trees'
    strength = 1
    skill_level_required = 1
    path_to_icon = 'images/copper axe.jpg'
    sell_price = 75
    buy_price = 200

    def __init__(self):
        super().__init__()


class SteelAxe(Axe):
    # Concrete axe item for Steel Axe

    title = 'Steel Axe'
    description = 'Steel Axe for chopping down trees'
    strength = 3
    skill_level_required = 5
    path_to_icon = 'images/steel axe.jpg'
    sell_price = 125
    buy_price = 500

    def __init__(self):
        super().__init__()


class MithrilAxe(Axe):
    # Concrete axe item for Mithril Axe

    title = 'Mithril Axe'
    description = 'Mithril Axe for chopping down trees'
    strength = 6
    skill_level_required = 10
    path_to_icon = 'images/mithril axe.jpg'
    sell_price = 250
    buy_price = 1500

    def __init__(self):
        super().__init__()


class AdamantAxe(Axe):
    # Concrete axe item for Adamant Axe

    title = 'Adamant Axe'
    description = 'Adamant Axe for chopping down trees'
    strength = 10
    skill_level_required = 12
    path_to_icon = 'images/adamant axe.jpg'
    sell_price = 400
    buy_price = 2500

    def __init__(self):
        super().__init__()


class Pickaxe(Tool):
    # Abstract class to be subclassed by all instantiable mining pickaxe types, e.g. Copper Pickaxe, Steel Pickaxe, etc.

    def __init__(self):
        super().__init__()


class CopperPickaxe(Pickaxe):
    # Concrete pickaxe item for Copper pickaxe

    title = 'Copper Pickaxe'
    description = 'Copper Pickaxe for mining rocks'
    strength = 1
    skill_level_required = 1
    path_to_icon = 'images/copper pickaxe.jpg'
    sell_price = 75
    buy_price = 200

    def __init__(self):
        super().__init__()


class SteelPickaxe(Pickaxe):
    # Concrete pickaxe item for Steel pickaxe

    title = 'Steel Pickaxe'
    description = 'Steel Pickaxe for mining rocks'
    strength = 3
    skill_level_required = 5
    path_to_icon = 'images/steel pickaxe.jpg'
    sell_price = 125
    buy_price = 500

    def __init__(self):
        super().__init__()


class MithrilPickaxe(Pickaxe):
    # Concrete pickaxe item for Mithril pickaxe

    title = 'Mithril Pickaxe'
    description = 'Mithril Pickaxe for mining rocks'
    strength = 6
    skill_level_required = 10
    path_to_icon = 'images/mithril pickaxe.jpg'
    sell_price = 250
    buy_price = 1500

    def __init__(self):
        super().__init__()


class AdamantPickaxe(Pickaxe):
    # Concrete pickaxe item for Adamant pickaxe

    title = 'Adamant Pickaxe'
    description = 'Adamant Pickaxe for mining rocks'
    strength = 10
    skill_level_required = 12
    path_to_icon = 'images/adamant pickaxe.jpg'
    sell_price = 400
    buy_price = 2500

    def __init__(self):
        super().__init__()


# Define list of all item types that can be instantiated, i.e. items that can appear in the inventory, shops, bank, etc.
# They appear in the list in the order they should appear in if sorted, e.g. in bank
concrete_types = [
    # Tools
    Tinderbox,
    Knife,
    # Axes
    CopperAxe,
    SteelAxe,
    MithrilAxe,
    AdamantAxe,
    # Pickaxes
    CopperPickaxe,
    SteelPickaxe,
    MithrilPickaxe,
    AdamantPickaxe,
    # Logs
    OakLog,
    WillowLog,
    MapleLog,
    YewLog,
    MagicLog,
    # Ores
    CopperOre,
    TinOre,
    CoalOre,
    IronOre,
    GoldOre,
    # Short bows
    OakShortbow,
    WillowShortbow,
    MapleShortbow,
    YewShortbow,
    MagicShortbow
]
