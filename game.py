import os
from map import Map
from shop import Shop
from bank import Bank
from skills import SkillSet
from inventory import Inventory
from status_bar import StatusBar
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QStackedLayout


class GameDisplayIndex:
    # Class to represent which index of the stacked game display is currently visible
    # Always updated whenever stacked game display layout changes to keep up to date with what's visible
    # We made it a class because we need to pass references to it around
    # We are asserting that the stacked layout currentIndex() will always equal the `.visible_index`

    def __init__(self):
        # Create a mapping from an object (reference) to what index it is in the stacked layout
        # `next_free_index` is the index to assign to a new object in `add_display`
        # Last viewed map helps us know what map to go back to, e.g. if we opened a shop in a cave, we need to
        # go back to display that exact cave when we close the shop, not the initial surface map

        # Set for the first time when we __getitem__ in Game's init to set game display initially to surface Map
        self.visible_index = None
        self.last_viewed_map_index = None

        self.next_free_index = 0
        self.obj_to_index = {}

    def add_display(self, obj):

        self.obj_to_index[obj] = self.next_free_index
        self.next_free_index += 1

    def __getitem__(self, item):
        # We assume by accessing the index of the object we are making it visible in the stacked layout

        index = self.obj_to_index[item]

        if isinstance(item, Map):
            self.last_viewed_map_index = index

        self.visible_index = index
        return index

    def calculate_inverse_mapping(self):
        # Helps us get the object that is currently visible, by indexing inverse mapping on visible index

        self.index_to_obj = {self.obj_to_index[key]: key for key in self.obj_to_index}

    def is_map_visible(self):

        return isinstance(self.index_to_obj[self.visible_index], Map)

    def get_last_viewed_map(self):
        # If map visible, we can assume the last viewed map is the visible one
        # If map not visible, the last viewed map is the one we had visible when we opened a new display (e.g. shop)

        last_visible_map = self.index_to_obj[self.last_viewed_map_index]
        assert isinstance(last_visible_map, Map)
        return last_visible_map

    def is_shop_visible(self):

        return isinstance(self.index_to_obj[self.visible_index], Shop)

    def get_visible_shop(self):

        assert self.is_shop_visible()
        return self.index_to_obj[self.visible_index]

    def is_bank_visible(self):

        return isinstance(self.index_to_obj[self.visible_index], Bank)

    def get_visible_bank(self):

        assert self.is_bank_visible()
        return self.index_to_obj[self.visible_index]


class Game(QMainWindow):

    # It is hard to dynamically create pyqtSignals, so we manually define one for each map.
    # Each map needs a unique signal, which is emitted on whenever a valid key is pressed when that map is visible.
    # It connects to that map's `on_key_pressed_event` slot for it to handle, and not the other maps.
    # E.g. if the surface is visible, and we press an arrow key to move, we want the surface Map object to handle it,
    # so on detecting a key press, we emit on the signal related to which map is visible (if a map is visible)
    key_pressed_cave = pyqtSignal(int)
    key_pressed_surface = pyqtSignal(int)
    key_pressed_lower_cave = pyqtSignal(int)

    # Signal we pass around the codebase to update the status bar under the game display with relevant game logging
    status_bar_signal = pyqtSignal(str)

    def __init__(self):

        super().__init__()

        # Game timer emits every game tick (1 sec)
        # Connect to every slot that needs a game tick, e.g. trees regenerating after x ticks, or NPCs moving every tick
        self.timer = QTimer()

        self.setWindowTitle("StarScape")
        self.setFixedSize(QSize(1600, 900))

        self.status_bar = StatusBar()
        self.status_bar_signal.connect(self.status_bar.update_status_bar)

        # Create stacked layout for the main game display, which alternates between map displays, shop displays, etc.
        # Corresponding index object keeps a mapping from the widget object to the relevant index in the stacked layout,
        # as well as keeping track of which one is currently visible, and the last visible map object
        self.stacked_game_display_layout = QStackedLayout()
        self.stacked_game_display_index = GameDisplayIndex()

        self.skills = SkillSet(self.status_bar_signal)
        self.inventory = Inventory(self.skills, self.stacked_game_display_index, self.status_bar_signal)

        # For every json file in 'maps/', create a new Map object, connect the relevant signals & slots, add to
        # stacked layout and custom index mapper, etc.
        # We keep a mapping from map name to corresponding Map object (e.g. 'surface' -> Map obj for surface)
        # This is used to help us transport between different maps. Transport tiles emit the str of the map
        # they are to transport to, so we can index in this dictionary to get the object, then set stacked layout to it
        self.map_name_to_obj = {}

        # Map the manually defined pyqtSignals to the map name
        # Whenever creating new map area, we have to manually add a new pyqtSignal out of init, and add to dict here
        self.key_pressed_signals = {
            'cave': self.key_pressed_cave,
            'surface': self.key_pressed_surface,
            'lower_cave': self.key_pressed_lower_cave
        }

        map_names = [f.replace('.json', '') for f in os.listdir('maps') if f.endswith('.json')]
        for map_name in map_names:

            map_obj = Map(
                map_name=map_name,
                path_to_map_json=os.path.join('maps', map_name + '.json'),
                inventory=self.inventory,
                skills=self.skills,
                timer=self.timer,
                status_bar_signal=self.status_bar_signal
            )

            self.map_name_to_obj[map_name] = map_obj
            self.key_pressed_signals[map_name].connect(map_obj.on_key_press_event)

            map_obj.shop_clicked.connect(self.change_stacked_game_display)
            map_obj.bank_clicked.connect(self.change_stacked_game_display_to_bank)
            map_obj.transport_clicked.connect(self.change_stacked_game_display_between_maps)

            self.stacked_game_display_layout.addWidget(map_obj)
            self.stacked_game_display_index.add_display(map_obj)

        # Create the bank instance shared across the game (different chests, on different maps, access the same bank)
        self.bank = Bank(self.inventory, self.status_bar_signal)
        self.bank.close_button.clicked.connect(self.change_stacked_game_display_to_map)
        self.stacked_game_display_layout.addWidget(self.bank)
        self.stacked_game_display_index.add_display(self.bank)

        # For each skill instance, add the information widget to the stacked layout display, and connect signals
        for skill_type in self.skills.skills:
            skill = self.skills.skills[skill_type]
            skill.skill_clicked_on.connect(self.change_stacked_game_display)
            skill.information_widget.close_button.clicked.connect(self.change_stacked_game_display_to_map)
            self.stacked_game_display_layout.addWidget(skill.information_widget)
            self.stacked_game_display_index.add_display(skill.information_widget)

        # For all the shop instances across the different maps:
        # - add to the stacked layout and work out relevant display index
        # - connect the close button to slot for changing back to map display
        for map_name in self.map_name_to_obj:
            for shop in self.map_name_to_obj[map_name].shops:
                shop.set_inventory_reference(self.inventory)
                shop.close_button.clicked.connect(self.change_stacked_game_display_to_map)
                self.stacked_game_display_layout.addWidget(shop)
                self.stacked_game_display_index.add_display(shop)

        # We define the starting map as 'surface.json', set initial display to here, and add player
        # We are asserting that whatever map is visible, the player is on it
        initial_map = self.map_name_to_obj['surface']
        self.stacked_game_display_layout.setCurrentIndex(self.stacked_game_display_index[initial_map])
        initial_map.insert_player(2, 2)

        # Once we've added all layouts to stacked layout, work out a reverse mapping in the index tracker
        self.stacked_game_display_index.calculate_inverse_mapping()

        overall_layout = QHBoxLayout()
        left_panel_layout = QVBoxLayout()
        right_panel_layout = QVBoxLayout()

        left_panel_layout.addWidget(self.inventory)
        left_panel_layout.addWidget(self.skills)

        right_panel_layout.addLayout(self.stacked_game_display_layout)
        right_panel_layout.addWidget(self.status_bar)

        overall_layout.addLayout(left_panel_layout)
        overall_layout.addLayout(right_panel_layout)

        # To add layout to the window we need to apply it to a dummy widget to then use .setCentralWidget
        # to apply widget and layout to the window
        widget = QWidget()
        widget.setLayout(overall_layout)
        self.setCentralWidget(widget)

        # Set game timer to tick every 1s (1000ms)
        self.timer.start(1000)

    def mouseReleaseEvent(self, e):
        # We will .ignore() in any place to bubble up to here, so we can clear the currently selected item in inventory

        self.inventory.deselect_item()

    def keyPressEvent(self, e):

        # If we press any key, deselect current inventory item
        self.inventory.deselect_item()

        self.status_bar_signal.emit("")

        key_int = e.key()

        if key_int in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right] and self.stacked_game_display_index.is_map_visible():
            # Move player only if we're in map mode
            # We're assuming the player is on the visible map
            # Emit signal to the map that is visible to handle
            # If a map is visible, the last viewed one is the visible one
            visible_map = self.stacked_game_display_index.get_last_viewed_map()
            self.key_pressed_signals[visible_map.map_name].emit(key_int)

        elif key_int == Qt.Key_Escape and not self.stacked_game_display_index.is_map_visible():
            # If we press ESC and current display is not a map, go back to the last viewed map
            # Last viewed map means if we open a bank display, for example, in a cave, on pressing escape
            # we want to go back to viewing that exact cave, not some other map
            self.change_stacked_game_display_to_map()

    def change_stacked_game_display(self, obj):

        self.status_bar_signal.emit("")
        self.stacked_game_display_layout.setCurrentIndex(self.stacked_game_display_index[obj])

    def change_stacked_game_display_to_map(self):
        # Called whenever we want to change back to the last viewed map, when the map is not currently visible
        # e.g. pressing close button in bank display, or ESC key from skill information display

        last_map = self.stacked_game_display_index.get_last_viewed_map()
        self.change_stacked_game_display(last_map)

    def change_stacked_game_display_to_bank(self):

        self.change_stacked_game_display(self.bank)

    def change_stacked_game_display_between_maps(self, destination_str, destination_x, destination_y):
        # Called whenever we are changing between map displays, when a transport tile is clicked on
        # Takes a str representing which map we are changing to, and coordinates of where to land
        # We have a dictionary built for mapping from that str of map name to the relevant map object

        old_map = self.stacked_game_display_index.get_last_viewed_map()
        new_map = self.map_name_to_obj[destination_str]

        if new_map.can_insert_player(destination_x, destination_y):
            old_map.remove_player()
            self.change_stacked_game_display(new_map)
            new_map.insert_player(destination_x, destination_y)
        else:
            self.status_bar_signal.emit("Cannot move to this map - something is on the tile you're trying to move to! Try again in a second")


if __name__ == '__main__':

    # You need one and only one QApplication instance per application, which holds the event loop of the app
    app = QApplication([])

    game = Game()
    game.show()

    # Start the event loop
    app.exec_()
