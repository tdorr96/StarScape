import json
import random
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout
from tiles import code_to_feature, EmptyTile, ShopTile, Interactable, BankChestTile, NPC, TransportTile, Player, Fire


class Map(QWidget):
    # The largest widget on the right-hand panel, that displays the game we move around in and interact with

    # Signals emitted whenever we want to change the game display panel to:
    bank_clicked = pyqtSignal()          # - the (only) bank widget, by clicking on bank chest tile
    shop_clicked = pyqtSignal(object)    # - a (one of possible many unique) shop widgets, by clicking on a shopkeeper
    transport_clicked = pyqtSignal(str, int, int)  # - a different map by clicking on transport tile

    def __init__(self, map_name, path_to_map_json, inventory, skills, timer, status_bar_signal):

        super().__init__()

        self.width = 1300
        self.height = 850

        self.timer = timer
        self.skills = skills
        self.map_name = map_name
        self.inventory = inventory
        self.status_bar_signal = status_bar_signal

        self.setFixedSize(QSize(self.width, self.height))

        with open(path_to_map_json, 'r') as open_f:
            loaded_map = json.load(open_f)

        # The map is a large grid, and we store all the tiles in a list of lists `self.map`,
        # Index into list of lists as `self.map[y][x]`
        # All coordinates (tiles access, calculating distances, etc.) done wrt. `self.map`, i.e. absolute coordinates
        # .x and .y values of the tile objects are kept in sync with the index into where they are stored in `self.map`
        # We visually display a window around player, `self.player_window`, which is a grid layout
        # We re-draw this window grid layout any time tiles change, e.g. player moves,
        # and the absolute coordinates are mapped to grid coordinates here and here only
        # If we get to the boundary of the map and there isn't enough tiles around player to centre the player,
        # take a window number of tiles from boundary

        self.map = []
        self.map_rows = loaded_map['total']['height']
        self.map_cols = loaded_map['total']['width']

        self.window_rows = loaded_map['window']['height']
        self.window_cols = loaded_map['window']['width']

        # We do not handle window heights or widths larger than that of the map, e.g. very narrow long corridor
        # Would need some sort of placeholder padding around map that we cannot move onto or put things on
        assert self.window_cols <= self.map_cols
        assert self.window_rows <= self.map_rows

        # Assume window sizes are odd so it's even number of grids outside of player
        assert self.window_cols % 2 == 1
        assert self.window_rows % 2 == 1

        # There needs to be `window_rows` x `window_cols` tiles filling the widget display, hence the size as follows
        # All the tiles in the map need to have this width and height, but we only display the window amount
        self.tile_width = int(self.width/self.window_cols)
        self.tile_height = int(self.height/self.window_rows)

        # Boolean as to whether we can light fires on this map
        # E.g. we don't want to light fires in a cave, but we do on the surface
        self.can_light_fires_on_map = loaded_map['can_light_fires']

        self.background_color = loaded_map['background_color']

        # Maps by default have no player, we only add them either on init to the surface map,
        # or when transporting between maps (also remove from the map we transported from)
        self.player = None

        # Accumulates all the shop instances in the game, for Game object to access for the stacked game layout
        self.shops = []

        # Create the grid layout for the visible window around player we will display as this widget's layout
        self.player_window = QGridLayout()
        self.player_window.setContentsMargins(20, 20, 20, 20)
        self.player_window.setSpacing(2)
        self.setLayout(self.player_window)

        # Set to True once we've drawn for the first time
        # This is so we only remove from player window grid once we've drawn for the first time and it has elements
        self.drawn_initially = False

        # Populate the list of lists of tiles: the map

        assert len(loaded_map['map']) == self.map_rows

        for row_index, row in enumerate(loaded_map['map']):

            assert len(row) == self.map_cols

            row_of_tiles = []

            for col_index, col in enumerate(row):

                if col:
                    # There is text in the column, e.g. 'WT' = Willow Tree, 'GS' = General Shop, 'BC' = Bank Chest
                    # Use mapping from scenery code to type of that tile, then instantiate and add to map

                    if ':' in col:
                        # It's a transport tile, e.g. 'CEntrance:cave:x:y', or 'CExit:surface:x:y'
                        # Need to parse the transport tile type, then the string representing map it transports to
                        # and the coordinates of where to on that map
                        # Has a slightly different init signature than other tile types
                        # Has an optional skill requirement at end, e.g. 'CEntrance:cave:x:y:mining(5)'

                        parsed_col = col.split(':')
                        tile_type = code_to_feature[parsed_col[0]]
                        tile = tile_type(
                            x=col_index, y=row_index,
                            tile_width=self.tile_width,
                            tile_height=self.tile_height,
                            destination=parsed_col[1],
                            destination_x=parsed_col[2], destination_y=parsed_col[3],
                            requirements=parsed_col[4] if len(parsed_col) == 5 else None
                        )
                        assert isinstance(tile, TransportTile)
                        tile.clicked.connect(self.interactable_clicked_on)

                    else:
                        # Rest of instantiable tile types have the same init signature

                        tile_type = code_to_feature[col]
                        tile = tile_type(
                            x=col_index, y=row_index,
                            tile_width=self.tile_width,
                            tile_height=self.tile_height,
                            status_bar_signal=self.status_bar_signal
                        )

                        if isinstance(tile, ShopTile) or isinstance(tile, BankChestTile) or isinstance(tile, Interactable):
                            # Has a `.clicked` we need to connect
                            tile.clicked.connect(self.interactable_clicked_on)

                        if isinstance(tile, Interactable):
                            self.timer.timeout.connect(tile.regenerate)

                        if isinstance(tile, ShopTile):
                            self.shops.append(tile.shop)

                        if isinstance(tile, NPC):
                            self.timer.timeout.connect(tile.tick_move)
                            tile.move.connect(self.npc_move)

                    tile.setStyleSheet("background-color: %s;" % self.background_color)
                    row_of_tiles.append(tile)

                else:
                    # Set to an empty tile

                    tile = EmptyTile(x=col_index, y=row_index, tile_width=self.tile_width, tile_height=self.tile_height)
                    tile.setStyleSheet("background-color: %s;" % self.background_color)
                    row_of_tiles.append(tile)

            assert len(row_of_tiles) == self.map_cols

            self.map.append(row_of_tiles)

        assert(len(self.map)) == self.map_rows

    def calculate_window_range(self):
        # Calculate the square grid defining the window we display in the game map
        # Need to cap at the boundaries if window around player would extend past a map border

        # We only ever want to draw a window around player if this map has a player on it
        assert self.player is not None

        # Work out the row range

        player_y = self.player.y
        rows_either_side_of_player = int((self.window_rows - 1) / 2)

        if (player_y - rows_either_side_of_player) < 0:
            # Cap at top of map
            row_range = list(range(0, self.window_rows))

        elif (player_y + rows_either_side_of_player) >= self.map_rows:
            # Cap at bottom of map
            row_range = list(range(self.map_rows - self.window_rows, self.map_rows))

        else:
            # No cap necessary
            row_range = list(range(player_y - rows_either_side_of_player, player_y + rows_either_side_of_player + 1))

        # Work out the column range

        player_x = self.player.x
        cols_either_side_of_player = int((self.window_cols - 1) / 2)

        if (player_x - cols_either_side_of_player) < 0:
            # Cap at left of map
            col_range = list(range(0, self.window_cols))

        elif (player_x + cols_either_side_of_player) >= self.map_cols:
            # Cap at right of map
            col_range = list(range(self.map_cols - self.window_cols, self.map_cols))

        else:
            # No cap necessary
            col_range = list(range(player_x - cols_either_side_of_player, player_x + cols_either_side_of_player + 1))

        return col_range, row_range

    def redraw(self):
        # Populate the grid's layout with a window around player
        # Need to handle edge cases: if player near boundary and window would extend past: stop at boundary edge
        # We are assuming window fits within or fits exactly to map size (assert in init function)

        # We only ever want to draw a window around player if this map has a player on it
        assert self.player is not None

        # Remove all current grid items from grid layout to draw from scratch again
        # (if not drawing for the first time - empty grid to start with!)
        if self.drawn_initially:
            for window_row in range(self.window_rows):
                for window_col in range(self.window_cols):
                    grid_item = self.player_window.itemAtPosition(window_row, window_col)
                    self.player_window.removeItem(grid_item)
                    if grid_item is not None:
                        if grid_item.widget().isVisible():
                            grid_item.widget().setParent(None)
                            grid_item.widget().hide()

        # Add the widgets in the new window back to the grid
        # We need to map from the absolute coordinates of `self.map` to the grid coordinates of `self.player_window`

        col_range, row_range = self.calculate_window_range()

        assert len(col_range) == self.window_cols
        assert len(row_range) == self.window_rows

        top_left_x = col_range[0]
        top_left_y = row_range[0]

        for row_index in row_range:
            for col_index in col_range:
                self.player_window.addWidget(
                    self.map[row_index][col_index],
                    row_index-top_left_y,
                    col_index-top_left_x
                )
                self.map[row_index][col_index].show()

        if not self.drawn_initially:
            # If we've drawn for first time, from now on we need to remove all the items in grid on every re-draw
            self.drawn_initially = True

    def get_surroundings(self, x, y):
        # Return list of Tile objects, those in the four surroundings tiles from x, y absolute `self.map` coordinates

        surroundings = []

        for surrounding_x, surrounding_y in [(x+1, y), (x-1, y), (x, y-1), (x, y+1)]:

            if surrounding_x < 0 or surrounding_x >= self.map_cols:
                continue

            if surrounding_y < 0 or surrounding_y >= self.map_rows:
                continue

            surroundings.append(self.map[surrounding_y][surrounding_x])

        return surroundings

    def interactable_clicked_on(self, x, y):
        # Signal emitted from the tiles with `.clicked` pyqtSignals: Interactable, ShopTile, BankChestTile, etc.
        # The x and y coordinates refer to the absolute coordinates of `self.map`

        # We should only have clicked on the map if the player was on it
        assert self.player is not None

        # We want to clear the previous status bar if we try and interact with the game again (in a valid manner)
        self.status_bar_signal.emit("")

        surroundings = self.get_surroundings(x, y)

        # Check if player within one tile
        if not any(isinstance(s, Player) for s in surroundings):
            self.status_bar_signal.emit("Player not within one tile to interact - try moving closer")
            return

        tile = self.map[y][x]

        if isinstance(tile, ShopTile):
            # We clicked on a shop, emit signal to change stacked display to the relevant shop interface
            self.shop_clicked.emit(tile.shop)

        elif isinstance(tile, BankChestTile):
            # We clicked on a bank chest, emit signal to change stacked display to bank interface
            self.bank_clicked.emit()

        elif isinstance(tile, TransportTile):
            # We clicked on a transport tile, emit a signal with the string representing where we are transporting to
            # The main Game object has a mapping from map string names to Map objects
            # Some transport tiles will have skill requirements - check we meet all these first
            if self.skills.meets_requirements(tile.skill_requirements):
                self.transport_clicked.emit(tile.destination, tile.destination_x, tile.destination_y)
            else:
                self.status_bar_signal.emit("You don't have the skill requirements to enter here: %s" % tile.requirements_string)

        else:
            # If not interacting with a shop or a bank, it will be an interactable (tree or rock)
            # We only emit to this slot and interact if it was not depleted (i.e. has health and not waiting to regen)

            assert isinstance(tile, Interactable)
            tile.interact(self.inventory, self.skills)

    def swap_tile_positions(self, x1, y1, x2, y2):
        # Takes coordinates to two item positions in the map
        # Swaps them in map list of lists,
        # and updates x and y class variables of underlying tiles to represent the change
        # Make sure to redraw() after call to this function if they are within the player's visible window

        tile1 = self.map[y1][x1]
        tile2 = self.map[y2][x2]

        tile1.x, tile1.y = x2, y2
        tile2.x, tile2.y = x1, y1

        self.map[y1] = self.map[y1][:x1] + [tile2] + self.map[y1][x1+1:]
        self.map[y2] = self.map[y2][:x2] + [tile1] + self.map[y2][x2+1:]

    def on_key_press_event(self, key_int):

        # Should only have emitted to this slot if player was on it and the map was visible
        assert self.player is not None

        current_x, current_y = self.player.x, self.player.y

        # For each possible key press, check we're not on grid relevant boundary,
        # and work out adjacent tile trying to swap with

        if key_int == Qt.Key_Up:

            if current_y == 0:
                return

            adjacent_widget = self.map[current_y-1][current_x]

        elif key_int == Qt.Key_Down:

            if current_y == self.map_rows - 1:
                return

            adjacent_widget = self.map[current_y+1][current_x]

        elif key_int == Qt.Key_Left:

            if current_x == 0:
                return

            adjacent_widget = self.map[current_y][current_x-1]

        elif key_int == Qt.Key_Right:

            if current_x == self.map_cols - 1:
                return

            adjacent_widget = self.map[current_y][current_x+1]

        # Now we know we're not trying to move past boundary, see if the adjacent tile is empty and if so move
        # To move, we swap the tiles (i.e. position in map and underlying tile coordinates),
        # and then re-draw display window

        if isinstance(adjacent_widget, EmptyTile):

            self.swap_tile_positions(
                x1=current_x, y1=current_y,
                x2=adjacent_widget.x, y2=adjacent_widget.y
            )

            self.redraw()

    def npc_move(self, x, y):
        # This function is called every tick for each NPC in the map
        # It will be called even if the map is not visible on the stacked layout

        npc = self.map[y][x]

        # Calculate the possible moves for an NPC, in the form of the coordinates they would be after move
        # Options: No move, move up one, move down one, move left one, move right one
        # We can only move into an empty tile, and if we do not pass the NPC's maximum radius, or map boundary condition
        move_options = [(x, y)]  # start with a no move option

        # Move left if not on boundary, not outside of NPCs wander radius, and it's an empty tile
        if x > 0 and isinstance(self.map[y][x-1], EmptyTile):
            if x >= npc.initial_x or (npc.initial_x - x) < npc.maximum_radius:
                move_options.append((x-1, y))

        # Move right if not on boundary, not outside of NPCs wander radius, and it's an empty tile
        if x < (self.map_cols - 1) and isinstance(self.map[y][x+1], EmptyTile):
            if x <= npc.initial_x or (x - npc.initial_x) < npc.maximum_radius:
                move_options.append((x+1, y))

        # Move up if not on boundary, not outside of NPCs wander radius, and it's an empty tile
        if y > 0 and isinstance(self.map[y-1][x], EmptyTile):
            if y >= npc.initial_y or (npc.initial_y - y) < npc.maximum_radius:
                move_options.append((x, y-1))

        # Move down if not on boundary, not outside of NPCs wander radius, and it's an empty tile
        if y < (self.map_rows - 1) and isinstance(self.map[y+1][x], EmptyTile):
            if y <= npc.initial_y or (y - npc.initial_y) < npc.maximum_radius:
                move_options.append((x, y+1))

        # Randomly pick an option and do the swapping
        random_move = random.choice(move_options)

        self.swap_tile_positions(
            x1=x, y1=y,
            x2=random_move[0], y2=random_move[1]
        )

        # Only re-draw the window grid around player if something moves into/out of/within the window
        # and of course, the player is on this map first and foremost
        # It will still change the underlying `self.map` representation and the Tile object's coordinates to keep in
        # line with `self.map` indices,
        # but only redraw the window if necessary: i.e. if either the new or old coordinates are in the window grid
        # and they're not the same (i.e. don't redraw if chose the no-move option within the window)

        if self.player is None:
            return

        need_to_redraw = False
        col_range, row_range = self.calculate_window_range()

        for row in row_range:
            for col in col_range:

                if (col, row) == (x, y) or (col, row) == random_move:
                    # If either the new coord is in window or old coord is in window

                    if (x, y) != random_move:
                        # Only redraw if not moving to identical position
                        # Will set this True twice if we're moving within window with different coords, but that's fine
                        need_to_redraw = True

        if need_to_redraw:
            self.redraw()

    def can_insert_player(self, x, y):

        return isinstance(self.map[y][x], EmptyTile)

    def insert_player(self, x, y):

        assert self.can_insert_player(x, y)

        self.player = Player(
            x=x, y=y,
            tile_width=self.tile_width,
            tile_height=self.tile_height
        )
        self.player.setStyleSheet("background-color: %s;" % self.background_color)

        self.map[y][x].close()
        self.map[y][x].setParent(None)

        self.map[y][x] = self.player

        self.redraw()

    def remove_player(self):

        assert self.player is not None

        self.map[self.player.y][self.player.x].close()
        self.map[self.player.y][self.player.x].setParent(None)

        self.map[self.player.y][self.player.x] = EmptyTile(
            x=self.player.x, y=self.player.y,
            tile_width=self.tile_width, tile_height=self.tile_height
        )
        self.map[self.player.y][self.player.x].setStyleSheet("background-color: %s;" % self.background_color)

        self.player = None

    def can_light_fire(self):
        # To light a fire we move to the right after lighting it
        # We can only light one if there is an empty slot to the right (including checking not on far-right border)

        assert self.player is not None

        if not self.can_light_fires_on_map:
            return False

        if self.player.x + 1 >= self.map_cols:
            return False

        tile_to_right = self.map[self.player.y][self.player.x+1]

        if not isinstance(tile_to_right, EmptyTile):
            return False

        return True

    def light_fire(self, ticks_for_fire_to_disappear):
        # Swap player tile and tile to right, then replace the swapped empty tile with a Fire tile

        assert self.can_light_fire()

        self.swap_tile_positions(
            x1=self.player.x, y1=self.player.y,
            x2=self.player.x+1, y2=self.player.y
        )

        # Empty tile is now to left after swapping
        to_light_x, to_light_y = self.player.x-1, self.player.y

        fire_tile = Fire(
            x=to_light_x, y=to_light_y,
            tile_width=self.tile_width,
            tile_height=self.tile_height,
            ticks_for_fire_to_disappear=ticks_for_fire_to_disappear
        )
        self.timer.timeout.connect(fire_tile.count_down)
        fire_tile.remove_signal.connect(self.remove_fire)
        fire_tile.setStyleSheet("background-color: %s;" % self.background_color)

        self.map[to_light_y][to_light_x].close()
        self.map[to_light_y][to_light_x].setParent(None)

        self.map[to_light_y][to_light_x] = fire_tile

        self.redraw()

    def remove_fire(self, x, y):
        # Slot emitted to when a fire times out
        # Does not have to be the map the player is currently on

        fire = self.map[y][x]

        fire.close()
        fire.setParent(None)

        empty_tile = EmptyTile(x=x, y=y, tile_width=self.tile_width, tile_height=self.tile_height)
        empty_tile.setStyleSheet("background-color: %s;" % self.background_color)
        self.map[y][x] = empty_tile

        # Re-draw if the player is on this map and the fire's coordinates are in the window range

        if self.player is None:
            return

        need_to_redraw = False
        col_range, row_range = self.calculate_window_range()

        for row in row_range:
            for col in col_range:

                if (col, row) == (x, y):
                    need_to_redraw = True

        if need_to_redraw:
            self.redraw()
