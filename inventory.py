from PyQt5.QtGui import QPixmap
from utilities import generate_label
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from items import concrete_types, Item, Tool, CopperAxe, CopperPickaxe, Tinderbox, Knife, Resource
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QAction, QMenu


class InventorySlot(QLabel):
    # Label widget for a non-empty inventory slot, which basically wraps around an Item object
    # Has a right-click context menu, that displays selling/depositing various amounts depending on visible game display
    # Even though an InventorySlot wraps 1 item, it will pass the call back to Inventory, so we can sell/bank
    # more than 1 item from an InventorySlot just with a reference to the item type we are selling/banking

    # If we left-click on an item when the game map is visible, we are selecting the item
    # This will either highlight select if no other one selected,
    # or combine two items for interaction, e.g. if tinderbox already selected and now select log, make a fire
    # Emits (col, row) of item clicked on
    select_clicked = pyqtSignal(int, int)

    sell_slot_clicked = pyqtSignal(int, type)     # amount to sell x type of item to sell
    deposit_slot_clicked = pyqtSignal(int, type)  # amount to deposit x type of item to deposit

    def __init__(self, col, row, item, slot_width, slot_height, game_display_index, status_bar_signal):

        super().__init__()

        self.col, self.row = col, row

        self.item = item
        self.setFixedSize(QSize(slot_width, slot_height))

        self.game_display_index = game_display_index
        self.status_bar_signal = status_bar_signal

        self.setPixmap(QPixmap(self.item.path_to_icon).scaled(int(slot_width/2), int(slot_height/2), Qt.KeepAspectRatio))
        self.setAlignment(Qt.AlignCenter)

        # Create actions in advance to display in right-click menu

        self.sell_one_action = QAction("Sell 1", self)
        self.sell_one_action.triggered.connect(self.sell_one_clicked)

        self.sell_five_action = QAction("Sell 5", self)
        self.sell_five_action.triggered.connect(self.sell_five_clicked)

        self.sell_ten_action = QAction("Sell 10", self)
        self.sell_ten_action.triggered.connect(self.sell_ten_clicked)

        self.sell_all_action = QAction("Sell all", self)
        self.sell_all_action.triggered.connect(self.sell_all_clicked)

        self.deposit_one_action = QAction("Deposit 1", self)
        self.deposit_one_action.triggered.connect(self.deposit_one_clicked)

        self.deposit_five_action = QAction("Deposit 5", self)
        self.deposit_five_action.triggered.connect(self.deposit_five_clicked)

        self.deposit_ten_action = QAction("Deposit 10", self)
        self.deposit_ten_action.triggered.connect(self.deposit_ten_clicked)

        self.deposit_all_action = QAction("Deposit all", self)
        self.deposit_all_action.triggered.connect(self.deposit_all_clicked)

    def sell_one_clicked(self):

        self.sell_slot_clicked.emit(1, type(self.item))

    def sell_five_clicked(self):

        self.sell_slot_clicked.emit(5, type(self.item))

    def sell_ten_clicked(self):

        self.sell_slot_clicked.emit(10, type(self.item))

    def sell_all_clicked(self):
        # We don't know how many in inventory, so emit the maximum it could be, which is 28

        self.sell_slot_clicked.emit(28, type(self.item))

    def deposit_one_clicked(self):

        self.deposit_slot_clicked.emit(1, type(self.item))

    def deposit_five_clicked(self):

        self.deposit_slot_clicked.emit(5, type(self.item))

    def deposit_ten_clicked(self):

        self.deposit_slot_clicked.emit(10, type(self.item))

    def deposit_all_clicked(self):

        self.deposit_slot_clicked.emit(28, type(self.item))

    def contextMenuEvent(self, e):

        if self.game_display_index.is_shop_visible():
            # Only want to display selling actions if the game display is a shop

            self.status_bar_signal.emit("%s sells for %sg" % (self.item.title, self.item.sell_price))

            context = QMenu(self)
            context.addAction(self.sell_one_action)
            context.addAction(self.sell_five_action)
            context.addAction(self.sell_ten_action)
            context.addAction(self.sell_all_action)
            context.exec_(e.globalPos())

        elif self.game_display_index.is_bank_visible():
            # Only want to display depositing actions if game display is the bank

            self.status_bar_signal.emit("")

            context = QMenu(self)
            context.addAction(self.deposit_one_action)
            context.addAction(self.deposit_five_action)
            context.addAction(self.deposit_ten_action)
            context.addAction(self.deposit_all_action)
            context.exec_(e.globalPos())

    def mouseReleaseEvent(self, e):

        self.status_bar_signal.emit("")

        if self.game_display_index.is_map_visible():

            if e.button() == Qt.LeftButton:
                self.select_clicked.emit(self.col, self.row)
                e.accept()

            else:
                e.ignore()

        else:

            if e.button() == Qt.LeftButton:

                if self.game_display_index.is_shop_visible():
                    self.status_bar_signal.emit("%s sells for %sg" % (self.item.title, self.item.sell_price))

                elif self.game_display_index.is_bank_visible():
                    self.deposit_one_clicked()

            e.ignore()

    def highlight(self):
        # If this item is the selected item in the inventory, need to highlight

        self.setStyleSheet("background-color:lightyellow")

    def dehighlight(self):
        # If we un-selecting the item, un-highlight

        self.setStyleSheet("")


class EmptyInventorySlot(QLabel):
    # Label widget for an empty inventory slot, just a placeholder in inventory grid

    def __init__(self, slot_width, slot_height, status_bar_signal):

        super().__init__()

        self.setFixedSize(QSize(slot_width, slot_height))

        self.status_bar_signal = status_bar_signal

    def mouseReleaseEvent(self, e):

        self.status_bar_signal.emit("")
        e.ignore()


class GoldPouch(QWidget):

    # Different icons for gold depending on how large the gold quantity is (small, medium, large)
    path_to_small_icon = 'images/gold_small.jpg'    # 0 <= gold < 100
    path_to_medium_icon = 'images/gold_medium.jpg'  # 100 <= gold < 1000
    path_to_large_icon = 'images/gold_large.jpg'    # 1000 <= gold

    def __init__(self, width, height):

        super().__init__()

        self.width = width
        self.height = height

        self.setFixedSize(QSize(self.width, self.height))

        # Start with 100 gold
        self.gold = 100

        gold_layout = QHBoxLayout()

        self.image_label = QLabel("")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.text_label = generate_label("", 15)

        gold_layout.addWidget(self.image_label)
        gold_layout.addWidget(self.text_label)

        self.setLayout(gold_layout)

        # Create the pixmaps in advance for different sizes of gold coin images

        self.small_gold_pixmap = QPixmap(self.path_to_small_icon).scaled(
            QSize(int(self.width/3), int(self.height/3)), Qt.KeepAspectRatio
        )

        self.medium_gold_pixmap = QPixmap(self.path_to_medium_icon).scaled(
            QSize(int(self.width/3), int(self.height/3)), Qt.KeepAspectRatio
        )

        self.large_gold_pixmap = QPixmap(self.path_to_large_icon).scaled(
            QSize(int(self.width/3), int(self.height/3)), Qt.KeepAspectRatio
        )

        # Re-draw widget
        self.redraw()

    def redraw(self):
        # Update the gold's image and text in the QLabels

        self.text_label.setText("%sg" % str(self.gold))

        if 0 <= self.gold < 100:
            self.image_label.setPixmap(self.small_gold_pixmap)
        elif 100 <= self.gold < 1000:
            self.image_label.setPixmap(self.medium_gold_pixmap)
        else:
            self.image_label.setPixmap(self.large_gold_pixmap)

    def add_gold(self, amount):

        self.gold += amount
        self.redraw()

    def remove_gold(self, amount):

        self.gold -= amount
        assert self.gold >= 0
        self.redraw()

    def can_afford_to_buy(self, item_buy_price):
        # Returns how many of the item we can afford to buy based on the gold we have

        return int(self.gold/item_buy_price)


class Inventory(QWidget):
    # An inventory holds a collection of instantiated concrete item types, i.e. resources or tools
    # It has a maximum inventory size of 28, methods to remove and add items, get tools in the inventory, etc.
    # It is also a widget that appears in the top left panel, and is visualised as a display grid of 28 icons
    # The inventory is stored as a grid layout, with each grid an inventory slot, that is either
    # - An empty slot placeholder
    # - An item slot, which is basically a wrapper around an Item object

    def __init__(self, skills, game_display_index, status_bar_signal):

        super().__init__()

        self.total_width = 300
        self.total_height = 600

        self.skills = skills
        self.game_display_index = game_display_index
        self.status_bar_signal = status_bar_signal

        # Set size of whole inventory widget
        self.setFixedSize(QSize(self.total_width, self.total_height))

        # Height of the text "INVENTORY" label
        self.text_height = 50

        # Take off the text height from the grid's height
        self.grid_height = self.total_height - self.text_height

        self.rows = 7
        self.cols = 4
        self.inventory_size = self.rows * self.cols

        # Work out dimensions of each slot in the 7 x 4 grid
        self.slot_width = int(self.total_width/self.cols)
        self.slot_height = int(self.grid_height/self.rows)

        # An inventory is represented as a 7 x 4 grid, with each grid either:
        # - an inventory slot wrapping around an Item object
        # - an empty inventory slot that's just a placeholder
        self.inventory = QGridLayout()
        self.inventory.setContentsMargins(10, 10, 10, 10)
        self.inventory.setSpacing(2)

        # An item in the inventory may have been selected, so keep track of which that item is
        # `selected` is either a coordinate (col, row), or None
        # Start out with nothing selected
        # Selection happens in two: set `self.selected` and highlight the corresponding slot (similarly for reverse)
        self.selected = None

        # A fresh inventory has a copper axe, a copper pickaxe, a tinderbox, and a knife
        init_items = [CopperAxe(), CopperPickaxe(), Tinderbox(), Knife()]
        for init_index in range(len(init_items)):

            init_col, init_row = init_index % 4, int(init_index/4)

            init_slot = InventorySlot(
                col=init_col, row=init_row,
                item=init_items[init_index],
                slot_width=self.slot_width, slot_height=self.slot_height,
                game_display_index=self.game_display_index,
                status_bar_signal=self.status_bar_signal
            )

            init_slot.sell_slot_clicked.connect(self.sell)
            init_slot.deposit_slot_clicked.connect(self.deposit)
            init_slot.select_clicked.connect(self.inventory_item_selected)

            self.inventory.addWidget(init_slot, init_row, init_col)

        # Fill remaining slots with empty inventory placeholder slots
        for i in range(len(init_items), self.inventory_size):

            col, row = i % 4, int(i/4)
            self.inventory.addWidget(EmptyInventorySlot(self.slot_width, self.slot_height, self.status_bar_signal), row, col)

        # Put bold 'Inventory' and the gold pouch above the grid

        overall_layout = QVBoxLayout()
        overall_layout.setContentsMargins(5, 5, 5, 5)
        overall_layout.setSpacing(1)

        top_layout = QHBoxLayout()

        top_layout.addWidget(generate_label("INVENTORY", 20, w=int(self.total_width/2), h=self.text_height))

        self.gold_pouch = GoldPouch(width=int(self.total_width/2), height=self.text_height)
        top_layout.addWidget(self.gold_pouch)

        overall_layout.addLayout(top_layout)
        overall_layout.addLayout(self.inventory)

        self.setLayout(overall_layout)

    def number_items(self):
        # Returns number of items in the inventory, i.e. the number of non-empty inventory slots

        count = 0

        for i in range(self.inventory_size):

            col, row = i % 4, int(i / 4)
            slot = self.inventory.itemAtPosition(row, col).widget()
            if type(slot) == InventorySlot:
                count += 1

        return count

    def is_full(self):

        return self.number_items() == self.inventory_size

    def space_for(self):

        return self.inventory_size - self.number_items()

    def get_tool(self, tool_type, skill_set=None):
        # Return a reference to the best tool of the specified type in our inventory (i.e. one with highest strength)
        # If we specify a skill set we also want to only get a tool that we can use (i.e. have skill level for)
        #
        # Behaviour:
        # - If there are multiple tools of the same type, get the first one appearing in the inventory
        # - If there are mixed tool types (e.g. tool type was an abstract class), then return a reference to the
        #   tool with the highest strength.
        # - Returns None if no tool in inventory
        #
        # E.g. if we're trying to get any axe type (i.e. `tool_type` is the abstract class Axe), return the axe
        # (Copper, Steel, or Mithril) in the inventory with the highest strength, ordered first in the inventory.
        # If we also specify a skill set, we return the highest strength tool that we are actually able to use.

        assert issubclass(tool_type, Tool)  # Restricting our item type to tools

        best_tool = None  # Keep track of best tool (i.e. highest strength we can use based on skills) seen so far

        for i in range(self.inventory_size):

            col, row = i % 4, int(i / 4)
            slot = self.inventory.itemAtPosition(row, col).widget()

            if type(slot) == EmptyInventorySlot:
                continue

            item = slot.item

            if isinstance(item, tool_type):
                if best_tool is None or item.strength > best_tool.strength:
                    # Python uses short-circuit logic evaluation
                    # True if (i) best_tool is None, or (ii) best_tool is not None and x's strength is better
                    if skill_set is None:
                        best_tool = item
                    else:
                        if skill_set.can_use(item):
                            best_tool = item

        return best_tool

    def add_to(self, items):
        # Takes a list of Item objects, and adds to the inventory
        # They need to be wrapped in inventory slot wrappers to fit in grid layout

        # We should only be adding a (non-zero) amount that will fit, i.e. <= space for
        # Check all items in list instances of concrete item types i.e. instance of Copper Axe, not the type Copper Axe
        assert 0 < len(items) <= self.space_for()
        assert all(type(x) in concrete_types for x in items)

        # Keep a pointer to inventory grid, to scan where next empty inventory slot is to know where to insert
        inventory_index = 0
        inventory_col, inventory_row = 0, 0
        inventory_slot = self.inventory.itemAtPosition(inventory_row, inventory_col)

        for item in items:

            # Find next available empty inventory slot to insert item into
            while type(inventory_slot.widget()) != EmptyInventorySlot:
                inventory_index += 1
                inventory_col, inventory_row = inventory_index % 4, int(inventory_index / 4)
                inventory_slot = self.inventory.itemAtPosition(inventory_row, inventory_col)

            # Insert item into this position by removing empty widget there and inserting new inventory item slot
            # Then move pointer to next grid position

            inventory_slot.widget().close()
            self.inventory.removeItem(inventory_slot)

            item_slot = InventorySlot(inventory_col, inventory_row, item, self.slot_width, self.slot_height, self.game_display_index, self.status_bar_signal)
            item_slot.sell_slot_clicked.connect(self.sell)
            item_slot.deposit_slot_clicked.connect(self.deposit)
            item_slot.select_clicked.connect(self.inventory_item_selected)
            self.inventory.addWidget(item_slot, inventory_row, inventory_col)

            inventory_index += 1
            inventory_col, inventory_row = inventory_index % 4, int(inventory_index / 4)
            inventory_slot = self.inventory.itemAtPosition(inventory_row, inventory_col)

    def deposit_all(self):
        # Slot connected to bank's 'deposit all' button

        # Work out how many of each item type in inventory
        # Python dictionaries in this Python version are insertion ordered
        # This means it deposits all of each item type, in the order of item types depending on when first one was found
        # This has implications for if bank does not have enough space for all the item types (read below)
        type_count = {}

        for i in range(self.inventory_size):

            col, row = i % 4, int(i/4)
            slot = self.inventory.itemAtPosition(row, col)

            if type(slot.widget()) == EmptyInventorySlot:
                continue

            item_type = type(slot.widget().item)
            if item_type in type_count:
                type_count[item_type] += 1
            else:
                type_count[item_type] = 1

        # We re-compute whether there is space for each item type on each call to `self.deposit`
        # If we can only fit some of the item types from deposit all, it will stop when it's full of types
        # (but add all the items of the types it did manage to fit before got full)
        # E.g. if the inventory is 1 Oak Log, then 1 Willow Log, then 26 Oak logs,
        # and bank has space for 1 type, with no oak or willow logs currently in any of its slots
        # It will add 27 oak logs (it found that type first), then fail to add the 1 willow log
        # An alternative approach was to use abstract classes: `self.deposit(28, Item)`, but this will not work -
        # We need to re-calculate if there is space in the bank for each item type
        for item_type in type_count:
            self.deposit(type_count[item_type], item_type)

    def remove_from(self, amount, item_type):
        # Removes, and returns, a specified amount of items of a specified type
        # If we request more than we have in the inventory of the type, it will just return as many as it can (i.e. all)
        # Will work on abstract classes, e.g. you could remove the first 10 axes in the inventory (regardless of
        # specific material i.e. copper, steel, mithril) by passing `amount` as 10 and `item_type` as abstract class Axe

        assert amount > 0
        assert issubclass(item_type, Item)

        # Keep removing items of specified type until we reach the end of inventory, or reach the limit `amount`
        removed_items = []

        for i in range(self.inventory_size):

            if len(removed_items) == amount:
                break

            # Still looking for items

            col, row = i % 4, int(i / 4)
            slot = self.inventory.itemAtPosition(row, col)

            if type(slot.widget()) == EmptyInventorySlot:
                continue

            if isinstance(slot.widget().item, item_type):
                # Add the reference to the actual item, not slot wrapper

                removed_items.append(slot.widget().item)

                # Remove inventory slot wrapper and replace with an empty inventory slot
                slot.widget().close()
                self.inventory.removeItem(slot)

                empty_slot = EmptyInventorySlot(self.slot_width, self.slot_height, self.status_bar_signal)
                self.inventory.addWidget(empty_slot, row, col)

        return removed_items

    def sell(self, amount, item_type_to_sell):
        # If we request to sell more than we have, `self.remove_from()` will cap at what we have in the inventory

        shop = self.game_display_index.get_visible_shop()

        if not shop.space_for(item_type_to_sell):
            # Check if there is space in the shop (i.e. there's a slot for items of this type already or at least
            # one empty slot to start a new item slot in)
            self.status_bar_signal.emit("Shop has no space for a new item type - cannot sell")
            return

        # Do the transaction - remove from inventory, add to shop, increase gold
        items_to_sell = self.remove_from(amount, item_type_to_sell)
        gold_made = shop.sell_to(items_to_sell)
        self.gold_pouch.add_gold(gold_made)

        self.status_bar_signal.emit("")

    def deposit(self, amount, item_type_to_deposit):
        # If we request to deposit more than we have, `self.remove_from()` will cap at what we have in the inventory

        bank = self.game_display_index.get_visible_bank()

        if not bank.space_for(item_type_to_deposit):
            # Check if space in bank, i.e. there's a slot for items of this type already, or at least one empty slot
            self.status_bar_signal.emit("Bank is full - cannot deposit")
            return

        # Do the transaction - remove from inventory, add to bank
        items_to_deposit = self.remove_from(amount, item_type_to_deposit)
        bank.deposit_to(items_to_deposit)

        self.status_bar_signal.emit("")

    def inventory_item_selected(self, col, row):
        # If an inventory item is selected (i.e. left-clicked in map mode), cases:
        # - if no other item currently selected, select and highlight this one
        # - if another item already selected, and we clicked the same one, deselect and de-highlight
        # - if another item already selected, and we click a different one, try combine them in a meaningful way
        #   (one has to be a tool, the other a resource).
        # Logic for handling item selection is handled in this `Inventory` class
        # `InventorySlot` class just has a highlight/de-highlight method, and a signal to emit to this slot

        if self.selected is None:
            # Nothing currently selected, so select whatever we clicked

            self.selected = (col, row)
            self.inventory.itemAtPosition(row, col).widget().highlight()

        else:
            # Something already selected

            if self.selected == (col, row):
                # Clicking same one as already selected

                self.deselect_item()

            else:
                # Something is already selected, and it's a different item from the one already selected
                # We can try and combine them if one is a Tool, and the other a Resource

                currently_selected = self.inventory.itemAtPosition(self.selected[1], self.selected[0])
                newly_selected = self.inventory.itemAtPosition(row, col)

                current_item = currently_selected.widget().item
                new_item = newly_selected.widget().item

                # Figure out if one is a tool and the other is a resource
                # and if so, which is the currently highlighted one

                tool_currently_selected = None
                tool_item, tool_grid_item = None, None
                resource_item, resource_grid_item = None, None

                if isinstance(current_item, Tool) and isinstance(new_item, Resource):
                    tool_currently_selected = True
                    tool_item, tool_grid_item = current_item, currently_selected
                    resource_item, resource_grid_item = new_item, newly_selected

                elif isinstance(current_item, Resource) and isinstance(new_item, Tool):
                    tool_currently_selected = False
                    tool_item, tool_grid_item = new_item, newly_selected
                    resource_item, resource_grid_item = current_item, currently_selected

                if tool_item is None and resource_item is None:
                    # The pair of items we clicked are not a tool and a resource (in either order)
                    self.status_bar_signal.emit("Try using a tool on a resource instead")
                    self.deselect_item()

                else:
                    # We clicked on a tool and a resource (in either order), do the combining

                    result = tool_item.process(
                        skills=self.skills,
                        resource=resource_item,
                        visible_map=self.game_display_index.get_last_viewed_map()
                    )

                    if result['success']:
                        # We could combine the items, now see if we need to remove / replace the resource

                        if result['action'] == 'remove':
                            # Remove the resource, e.g. tinderbox lighted a log and log needs to disappear

                            removed_col, removed_row = resource_grid_item.widget().col, resource_grid_item.widget().row

                            resource_grid_item.widget().close()
                            self.inventory.removeItem(resource_grid_item)

                            empty_slot = EmptyInventorySlot(self.slot_width, self.slot_height, self.status_bar_signal)
                            self.inventory.addWidget(empty_slot, removed_row, removed_col)

                        else:

                            assert result['action'] == 'replace'

                            # Replace the resource with whatever the tool made with it
                            # e.g. log made into a shortbow using a knife

                            replaced_col, replaced_row = resource_grid_item.widget().col, resource_grid_item.widget().row

                            resource_grid_item.widget().close()
                            self.inventory.removeItem(resource_grid_item)

                            replaced_slot = InventorySlot(
                                col=replaced_col, row=replaced_row,
                                item=result['generated_item'],
                                slot_width=self.slot_width, slot_height=self.slot_height,
                                game_display_index=self.game_display_index,
                                status_bar_signal=self.status_bar_signal
                            )

                            replaced_slot.sell_slot_clicked.connect(self.sell)
                            replaced_slot.deposit_slot_clicked.connect(self.deposit)
                            replaced_slot.select_clicked.connect(self.inventory_item_selected)

                            self.inventory.addWidget(replaced_slot, replaced_row, replaced_col)

                        # Need to deselect whatever item was selected
                        if tool_currently_selected:
                            # Set selected to None and de-higlight tool
                            self.deselect_item()
                        else:
                            # the selected resource item slot will have been removed/replaced, nothing to de-highlight
                            # just set the inventory's selected item to None
                            self.selected = None

                    else:
                        # We could not combine the items, log the reason why
                        self.status_bar_signal.emit(result['message'])
                        self.deselect_item()

    def deselect_item(self):
        # If there is a currently selected item, deselect it and un-highlight
        # This can be called from Game.mouseReleaseEvent, which is why all our mouseReleaseEvents have .ignore()
        # to bubble up the call and deselect an item if we interact with the game in a way which should deselect item
        # E.g. if we have an item selected, and we move the player, deselect the item
        # The only time we .accept() a mouseReleaseEvent is in InventorySlot if we left-click in map-mode, which
        # emits to `self.inventory_item_selected()` instead, to let us decide how to handle selection/deselection

        if self.selected is not None:
            self.inventory.itemAtPosition(self.selected[1], self.selected[0]).widget().dehighlight()
            self.selected = None
