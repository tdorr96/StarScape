from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from skill_information import SkillInformation
from items import CopperAxe, SteelAxe, MithrilAxe, AdamantAxe
from items import CopperOre, TinOre, CoalOre, IronOre, GoldOre
from items import OakLog, WillowLog, MapleLog, YewLog, MagicLog
from tiles import CopperRock, TinRock, CoalRock, IronRock, GoldRock
from tiles import OakTree, WillowTree, MapleTree, YewTree, MagicTree
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from items import OakShortbow, WillowShortbow, MapleShortbow, YewShortbow, MagicShortbow
from items import CopperPickaxe, SteelPickaxe, MithrilPickaxe, AdamantPickaxe, Tinderbox, Knife


class Skill(QWidget):
    # Abstract base class representing a Skill object
    # All skills share the same experience and levelling code, but they have their own (static) information

    # Emit to Game object when we click on this skill, to switch the main display widget to a skill information widget
    skill_clicked_on = pyqtSignal(object)

    def __init__(self):

        super().__init__()

        # Start with level 1 and only 1 xp, and the next level requires 100 xp
        self.level = 1
        self.experience = 1
        self.next_level_experience = 100

        # Arrange layout of widget (icon image and string of level & experience)
        self.text_label = QLabel("%s (%s xp)" % (self.level, self.experience))
        font = self.text_label.font()
        font.setPointSize(15)
        self.text_label.setFont(font)
        self.text_label.setAlignment(Qt.AlignCenter)

        image_label = QLabel("")
        image_label.setPixmap(QPixmap(self.path_to_icon))
        image_label.setAlignment(Qt.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(image_label)
        layout.addWidget(self.text_label)

        self.setLayout(layout)

    def update_skill_label(self):
        # When we gain xp, update the text representation of the skill to reflect xp/levels gained

        self.text_label.setText("%s (%s xp)" % (self.level, self.experience))

    def add_experience(self, xp):
        # Add experience to this skill object
        # If we reach the xp needed for the next level, increment the level and double experience for the level after
        # to keep it growing exponentially
        # It's possible we'll pass multiple levels at once, so keep incrementing level and next level xp as necessary
        # For an xp gain, generate a string, which says how many levels we gained, if we unlocked any new things, etc.
        # to output on the status bar for the user to see

        assert xp > 0

        self.experience += xp

        levels_gained = []  # Accumulates new levels we gained for updating status bar

        while self.experience >= self.next_level_experience:
            self.level += 1
            self.next_level_experience *= 2
            levels_gained.append(self.level)

        self.update_skill_label()

        output_status = ""
        if levels_gained:
            # Log how many levels we gained, and if we unlocked any new tools for use

            output_status = "%s %s level%s gained. " % (
                len(levels_gained), self.title, "" if len(levels_gained) == 1 else "s"
            )

            # Figure out if any new tools were unlocked based the skill levels we passed
            tools_unlocked = []
            for new_level in levels_gained:
                for tool in self.relevant_tools:
                    if new_level == tool.skill_level_required:
                        tools_unlocked.append(tool.title)

            if tools_unlocked:
                output_status += 'Tool%s unlocked: %s' % (
                    "" if len(tools_unlocked) == 1 else "s", ', '.join(tools_unlocked)
                )

        return output_status

    def __str__(self):

        return "%s: %s (%s xp)" % (self.title, self.level, self.experience)

    def __ge__(self, other):

        return self.level >= other

    def __lt__(self, other):

        return self.level < other

    def mouseReleaseEvent(self, e):
        # If we left-click on the skill's widget, replace the main game display widget with information about the skill

        if e.button() == Qt.LeftButton:
            self.skill_clicked_on.emit(self.information_widget)

        e.ignore()


class Woodcutting(Skill):
    # Concrete class for the Woodcutting skill

    title = 'Woodcutting'
    path_to_icon = 'images/woodcutting.jpg'
    relevant_tools_type = "Axes"
    relevant_tools = [CopperAxe, SteelAxe, MithrilAxe, AdamantAxe]
    relevant_interactables_type = 'Trees'
    # Map from the relevant interactable to the requirements needed to interact, be that a skill level or minimum tool
    # This is information needed for information widget
    relevant_interactables = {
        OakTree: OakTree.minimum_tool_required.title,
        WillowTree: WillowTree.minimum_tool_required.title,
        MapleTree: MapleTree.minimum_tool_required.title,
        YewTree: YewTree.minimum_tool_required.title,
        MagicTree: MagicTree.minimum_tool_required.title
    }
    # There are two ways to gain xp
    # - generating an item with a relevant tool (e.g. generating a log from chopping a tree with an axe)
    # - processing an item with a relevant tool (e.g. processing a log with a tinderbox to burn and remove it)
    xp_gain_per_generation = {
        OakLog: 50,
        WillowLog: 150,
        MapleLog: 400,
        YewLog: 600,
        MagicLog: 1000
    }
    xp_gain_per_process = {}

    def __init__(self):
        super().__init__()
        self.information_widget = SkillInformation(Woodcutting)


class Mining(Skill):
    # Concrete class for the Mining skill

    title = 'Mining'
    path_to_icon = 'images/mining.jpg'
    relevant_tools_type = "Pickaxes"
    relevant_tools = [CopperPickaxe, SteelPickaxe, MithrilPickaxe, AdamantPickaxe]
    relevant_interactables_type = 'Rocks'
    relevant_interactables = {
        CopperRock: CopperRock.minimum_tool_required.title,
        TinRock: TinRock.minimum_tool_required.title,
        CoalRock: CoalRock.minimum_tool_required.title,
        IronRock: IronRock.minimum_tool_required.title,
        GoldRock: GoldRock.minimum_tool_required.title
    }
    xp_gain_per_generation = {
        CopperOre: 40,
        TinOre: 40,
        CoalOre: 100,
        IronOre: 120,
        GoldOre: 200
    }
    xp_gain_per_process = {}

    def __init__(self):
        super().__init__()
        self.information_widget = SkillInformation(Mining)


class Firemaking(Skill):
    # Concrete class for the Firemaking skill

    title = 'Firemaking'
    path_to_icon = 'images/firemaking.jpg'
    relevant_tools_type = 'Tinderboxes'
    relevant_tools = [Tinderbox]
    relevant_interactables_type = 'Logs'
    relevant_interactables = {
        OakLog: "Level %s" % OakLog.firemaking_required,
        WillowLog: "Level %s" % WillowLog.firemaking_required,
        MapleLog: "Level %s" % MapleLog.firemaking_required,
        YewLog: "Level %s" % YewLog.firemaking_required,
        MagicLog: "Level %s" % MagicLog.firemaking_required
    }
    xp_gain_per_generation = {}
    xp_gain_per_process = {
        OakLog: 60,
        WillowLog: 100,
        MapleLog: 250,
        YewLog: 500,
        MagicLog: 750
    }

    def __init__(self):
        super().__init__()
        self.information_widget = SkillInformation(Firemaking)


class Fletching(Skill):
    # Concrete class for the Fletching skill

    title = 'Fletching'
    path_to_icon = 'images/fletching.jpg'
    relevant_tools_type = 'Knives'
    relevant_tools = [Knife]
    relevant_interactables_type = 'Logs'
    relevant_interactables = {
        OakLog: "Level %s" % OakLog.fletching_required,
        WillowLog: "Level %s" % WillowLog.fletching_required,
        MapleLog: "Level %s" % MapleLog.fletching_required,
        YewLog: "Level %s" % YewLog.fletching_required,
        MagicLog: "Level %s" % MagicLog.fletching_required
    }
    xp_gain_per_generation = {
        OakShortbow: 30,
        WillowShortbow: 100,
        MapleShortbow: 250,
        YewShortbow: 400,
        MagicShortbow: 600
    }
    xp_gain_per_process = {}

    def __init__(self):
        super().__init__()
        self.information_widget = SkillInformation(Fletching)


class SkillSet(QWidget):
    # Represents a collection of all the skills for the player, with one instance of each skill for each skill type
    # The overall skill collection is a widget, which contains each skill widget in vertical layout

    def __init__(self, status_bar_signal):

        super().__init__()

        self.status_bar_signal = status_bar_signal

        self.setFixedSize(QSize(300, 300))

        self.skills = {
            Mining: Mining(),
            Woodcutting: Woodcutting(),
            Firemaking: Firemaking(),
            Fletching: Fletching()
        }

        # Add each skill widget vertically
        layout = QVBoxLayout()

        for skill_type in self.skills:
            layout.addWidget(self.skills[skill_type])

        overall_layout = QVBoxLayout()

        skill_text_label = QLabel("SKILLS")
        font = skill_text_label.font()
        font.setPointSize(20)
        skill_text_label.setFont(font)
        skill_text_label.setAlignment(Qt.AlignCenter)
        skill_text_label.setFixedSize(QSize(300, 50))

        overall_layout.addWidget(skill_text_label)
        overall_layout.addLayout(layout)

        self.setLayout(overall_layout)

    def add_experience(self, items, generated):
        # Takes a list of items from an interaction, and parses the item types into xp gained in relevant skills
        # If `generated` True, the items we are parsing for xp have been generated in some way, e.g. obtained from tree
        # If `generated` is False, the items we are parsing have been processed, e.g. log burned
        # This affects which skills get what xp
        # Approach allows multiple skills to gain xp in an interaction, as well as same item give xp to multiple skills
        # Call `add_experience` for each skill only once, and string status signals from each call together
        # This avoids missing outputting a skill level gain in one if another was called after and overwrites the string

        assert len(items) > 0

        output_status = ""
        for skill_type in self.skills:

            xp_gained = 0
            skill = self.skills[skill_type]

            # Work out if we are adding xp for generated items or processed items
            # e.g. if generated is True and considering a log it was generated from a tree -> woodcutting xp
            # but if generated is False and considering a log it was processed with a tinderbox -> firemaking xp
            xp_map = skill.xp_gain_per_generation if generated else skill.xp_gain_per_process

            for item in items:

                if type(item) in xp_map:
                    xp_gained += xp_map[type(item)]

            if xp_gained > 0:
                output_status += skill.add_experience(xp_gained)

        self.status_bar_signal.emit(output_status)

    def can_use(self, tool):
        # We are assuming one and only one skill has this type of tool in its `relevant_tools` list
        # If we change to a tool requiring multiple skill levels in the future, will need to change together with all()

        for skill_type in self.skills:

            skill = self.skills[skill_type]

            if type(tool) in skill.relevant_tools:
                return skill >= tool.skill_level_required

    def can_burn(self, log):
        # Check our firemaking level meets minimum level needed to burn the log

        return self.skills[Firemaking] >= log.firemaking_required

    def can_fletch(self, log):
        # Check our fletching level meets minimum level needed to fletch the log

        return self.skills[Fletching] >= log.fletching_required

    def relevant_skill(self, tool):
        # Return the skill that lists this tool as it's relevant tool
        # Will only be one relevant skill for each tool

        for skill_type in self.skills:

            skill = self.skills[skill_type]

            if type(tool) in skill.relevant_tools:
                return skill

    def meets_requirements(self, skill_requirements):
        # Takes a dictionary, mapping from a string (that will be one of the skill classes .title's), to an integer
        # E.g. {'Mining': 5, 'Fletching': 10}
        # We need to check if we meet all the skill requirements specified in the dictionary
        # If dictionary is empty, will always return True

        for skill_type in self.skills:

            skill = self.skills[skill_type]

            if skill.title in skill_requirements:
                if skill < skill_requirements[skill.title]:
                    return False

        return True

    def __str__(self):

        return str([str(self.skills[skill_type]) for skill_type in self.skills])

    def __getitem__(self, item):

        return self.skills[item]
