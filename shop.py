from PyQt5.QtGui import QPixmap
from items import concrete_types
from utilities import generate_label
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QAction


class ShopSlot(QWidget):
    # Represents a slot in the shop's 10 x 10 item grid
    # ShopSlot a wrapper around a collection of instantiated items of the same type for sale,
    # Visually displayed in shop's grid as item icon, item name, and number in collection (i.e. how many for sale)
    # If there are no items in the collection, it's effectively an empty slot placeholder and has no visual display
    # Once added to the shop's grid, the slot object is permanently in that grid position, but by making the item list
    # empty/non-empty as we sell/buy it effectively alternates between empty placeholder or collection of sellable items

    slot_clicked = pyqtSignal(int, type)  # number to buy x type of item buying

    def __init__(self, slot_width, slot_height, status_bar_signal):
        # Shop Slots are always initialized empty

        super().__init__()

        self.slot_width = slot_width
        self.slot_height = slot_height

        self.status_bar_signal = status_bar_signal

        self.setFixedSize(QSize(self.slot_width, self.slot_height))

        # `self.items` and `self.item_type` either:
        # - an empty list and None if no items being stored here: empty placeholder for slot in shop
        # - or a list of the item instances and the concrete type of item objects in the list (guaranteed to be same)
        self.items = []
        self.item_type = None

        slot_layout = QVBoxLayout()

        self.item_image = QLabel("")
        self.text_label = generate_label("", 10)

        slot_layout.addWidget(self.item_image)
        slot_layout.addWidget(self.text_label)

        self.setLayout(slot_layout)

        # Create the QActions in advance to be used on right clicks

        self.buy_one_action = QAction("Buy 1", self)
        self.buy_one_action.triggered.connect(self.buy_one_clicked)

        self.buy_five_action = QAction("Buy 5", self)
        self.buy_five_action.triggered.connect(self.buy_five_clicked)

        self.buy_ten_action = QAction("Buy 10", self)
        self.buy_ten_action.triggered.connect(self.buy_ten_clicked)

        self.buy_all_action = QAction("Buy all", self)
        self.buy_all_action.triggered.connect(self.buy_all_clicked)

    def update_text_label(self):

        if len(self.items) == 0:
            # Empty, remove text
            self.text_label.setText("")

        else:
            # Not empty, so include text: item title x amount for sale
            self.text_label.setText("%s x %s" % (self.item_type.title, len(self.items)))

    def update_item_image(self):
        # Only call this method when we want to change the image, i.e.
        # empty -> non-empty (so add image): when adding
        # non-empty -> empty (so remove image): when removing

        if len(self.items) == 0:
            # Now empty, remove image
            self.item_image.clear()

        else:
            # Not empty, set image to the item's icon
            self.item_image.setPixmap(QPixmap(self.item_type.path_to_icon).scaled(
                QSize(int(self.slot_width / 3), int(self.slot_height / 3)), Qt.KeepAspectRatio
            ))
            self.item_image.setAlignment(Qt.AlignCenter)

    def is_empty_slot(self):
        # Is the slot not representing items for sale i.e. an empty placeholder

        return len(self.items) == 0

    def add_items(self, new_items):
        # We assume the types of all the new items we're adding are the same as the type this slot is representing
        # But we will check with an assert

        assert len(new_items) > 0

        if len(self.items) == 0:
            # Was empty, now need to make it not empty

            self.items.extend(new_items)
            self.item_type = type(self.items[0])

            # Only add an image if there wasn't something here before to save creating new QPixmaps constantly
            self.update_item_image()

        else:
            # Already items here, add to collection

            self.items.extend(new_items)

        # Update text in both cases, empty -> non-empty and non-empty -> non-empty
        self.update_text_label()

        # Check all the item types in this slot's item collection are the same after adding new items
        assert all(type(self.items[i]) == self.item_type for i in range(len(self.items)))

    def remove_items(self, amount):
        # Shop.buy_from() will only request an amount not more than what is in the shop slot
        # The `amount` passed in here will be the minimum of several quantities,
        # e.g. that amount we requested, what we can afford, space in inventory

        assert 0 < amount <= len(self.items)
        assert len(self.items) > 0

        removed_items = self.items[:amount]
        self.items = self.items[amount:]

        if len(self.items) == 0:
            # If no more items, make sure to set item type of shop slot to None
            # Only update image if we removed it, otherwise it would be the same and creating new QPixmaps constantly
            self.item_type = None
            self.update_item_image()

        # Update text label in both cases: non-empty -> empty and non-empty -> non-empty
        self.update_text_label()

        return removed_items

    def contextMenuEvent(self, e):

        if len(self.items) > 0:
            # Only want to right-click on shop slots that actually have items
            # Only add the actions we have the number of items for, e.g. don't add 'buy 10' if we only have 5 items

            self.status_bar_signal.emit("%s costs %sg to buy" % (self.item_type.title, self.item_type.buy_price))

            context = QMenu(self)
            context.addAction(self.buy_one_action)

            if len(self.items) >= 5:
                context.addAction(self.buy_five_action)

            if len(self.items) >= 10:
                context.addAction(self.buy_ten_action)

            if len(self.items) >= 2:
                context.addAction(self.buy_all_action)

            context.exec_(e.globalPos())

    def mouseReleaseEvent(self, e):
        # If we left-click on a non-empty shop slot, display the buy price in the status bar

        self.status_bar_signal.emit("")

        if e.button() == Qt.LeftButton and len(self.items) > 0:
            self.status_bar_signal.emit("%s costs %sg to buy" % (self.item_type.title, self.item_type.buy_price))

        e.ignore()

    def buy_one_clicked(self):

        self.slot_clicked.emit(1, self.item_type)

    def buy_five_clicked(self):

        self.slot_clicked.emit(5, self.item_type)

    def buy_ten_clicked(self):

        self.slot_clicked.emit(10, self.item_type)

    def buy_all_clicked(self):

        self.slot_clicked.emit(len(self.items), self.item_type)


class Shop(QWidget):
    # A widget representing a shop interface, that will replace main game map display when opened
    # There is one shop instance for each shop interface tile, so they have unique stock items
    # Each grid in the shop layout is a ShopSlot, that is either an empty placeholder,
    # or wraps a collection of non-zero items for sale
    # Guaranteed to be only one shop slot for each item type

    def __init__(self, shop_title, init_items, status_bar_signal):
        # Different shop types (e.g. general shop or blacksmith) may stock different initial items: `init_items`

        super().__init__()

        self.total_width = 1300
        self.total_height = 850

        self.status_bar_signal = status_bar_signal

        self.setFixedSize(QSize(self.total_width, self.total_height))

        self.text_height = 50

        self.grid_height = self.total_height - self.text_height

        self.rows = 10
        self.cols = 10
        self.shop_limit = self.rows * self.cols

        self.slot_width = int(self.total_width/self.cols)
        self.slot_height = int(self.grid_height/self.rows)

        self.shop = QGridLayout()
        self.shop.setContentsMargins(10, 10, 10, 10)
        self.shop.setSpacing(2)

        # Fill all the grid slots with empty shop slots
        for i in range(self.shop_limit):

            col, row = i % 10, int(i/10)
            empty_shop_slot = ShopSlot(self.slot_width, self.slot_height, self.status_bar_signal)
            empty_shop_slot.slot_clicked.connect(self.buy_from)
            self.shop.addWidget(empty_shop_slot, row, col)

        # Put bold 'SHOP' and a close button above grid layout

        overall_layout = QVBoxLayout()
        overall_layout.setContentsMargins(5, 5, 5, 5)
        overall_layout.setSpacing(1)

        top_layout = QHBoxLayout()

        self.close_button = QPushButton("close")
        self.close_button.setFixedSize(QSize(100, self.text_height))

        top_layout.addWidget(generate_label(shop_title.upper(), 30, w=1000, h=self.text_height))
        top_layout.addWidget(self.close_button)

        overall_layout.addLayout(top_layout)
        overall_layout.addLayout(self.shop)

        self.setLayout(overall_layout)

        # Add the initial stock items
        # Can handle the list containing items of different type, as we add lists of 1 item, one at a time
        for item in init_items:

            item_type = type(item)
            assert item_type in concrete_types

            # See if there is a slot for this item already; if so add there, otherwise add to the first new empty slot
            # We assume space in shop for all initial items (i.e. number of unique types <= the shop's limit)

            slot = self.find_item_type_slot(item_type)

            if slot is None:
                self.find_first_empty_slot().add_items([item])
            else:
                slot.add_items([item])

    def set_inventory_reference(self, inventory):
        # Will be called from main Game class after map initialization
        # Easier for shops to have reference to inventory, so can connect signals from ShopSlot directly to .buy_from()

        self.inventory = inventory

    def find_item_type_slot(self, item_type):
        # Searches all the slots to see if we have items of the type we are looking for stored in a shop slot
        # Will only ever pass in concrete types, not abstract types, so check types equal, not isinstance()
        # There will only ever be one slot for a given item type, so return first we find
        # Returns None if there is not a slot holding items of this type

        for i in range(self.shop_limit):

            col, row = i % 10, int(i/10)
            slot = self.shop.itemAtPosition(row, col).widget()

            if slot.item_type == item_type:
                return slot

        return None

    def find_first_empty_slot(self):
        # Searches the slots until we find an empty one (i.e. one with no items)
        # If there is no empty slot in the grid, return None

        for i in range(self.shop_limit):

            col, row = i % 10, int(i/10)
            slot = self.shop.itemAtPosition(row, col).widget()

            if len(slot.items) == 0:
                return slot

        return None

    def space_for(self, item_type):
        # There is space for an item type if either:
        # 1) there is already a slot in the grid holding this item type, in which case we can extend the items there
        # 2) if not, then there is at least one empty slot, where we can convert to a non-empty slot holding the items
        # Just because each slot in the shop has items in it, does not mean it's full
        # It's only full if there are no items of this type already where we can add to, *and* there are no empty slots
        # That's why `space_for` is parameterized by an item type

        if self.find_item_type_slot(item_type) is not None:
            return True

        if self.find_first_empty_slot() is not None:
            return True

        return False

    def sell_to(self, items_to_sell):
        # Takes a non-empty list of items, and adds to the shop's grid
        # - If already items of the same type in shop, add to that slot
        # - Otherwise, add to the first empty slot
        # We assume in this function we can sell the items, i.e. there is space_for() the item types

        # Check there is at least one item to sell, all the items are concrete item types
        assert len(items_to_sell) > 0
        assert all(type(x) in concrete_types for x in items_to_sell)

        # Get item type of items we're trying to sell, and check they're all the same type and there is a slot for them
        item_type_to_sell = type(items_to_sell[0])

        assert all(type(items_to_sell[i]) == item_type_to_sell for i in range(len(items_to_sell)))
        assert self.space_for(item_type_to_sell)

        # Search all the slots to see if we already have a slot for items of this type
        slot = self.find_item_type_slot(item_type_to_sell)

        if slot is None:
            # Need to make a new item type slot in grid - find the first empty slot, and add there
            # Guaranteed to be one as we checked for the space for above
            empty_slot = self.find_first_empty_slot()
            empty_slot.add_items(items_to_sell)

        else:
            # We are already selling it, just add items to the slot
            slot.add_items(items_to_sell)

        # Return gold made in selling to shop
        price_of_item = items_to_sell[0].sell_price
        return len(items_to_sell) * price_of_item

    def buy_from(self, amount, item_type_to_buy):
        # Item type guaranteed to already be in shop because we will have right-clicked on it and emitted to this slot

        if self.inventory.is_full():
            self.status_bar_signal.emit("Inventory full - cannot buy any items")
            return

        cost_of_item = item_type_to_buy.buy_price
        afford_to_buy = self.inventory.gold_pouch.can_afford_to_buy(cost_of_item)

        if afford_to_buy == 0:
            self.status_bar_signal.emit("Cannot afford to buy any of this item")
            return

        slot = self.find_item_type_slot(item_type_to_buy)
        assert slot is not None

        # We only want to buy exactly the amount we can manage, which depends on three factors
        # - the amount we actually requested - this amount is guaranteed to be in shop because only way buy_from()
        #   is called is by emitting from a shop slot right click, and the right click options dynamically show up
        #   depending on amount of items there is, e.g. won't offer "Buy 5" if only 4 items in stock
        # - the space in our inventory
        # - how many we can afford based on the gold we have
        amount_to_buy = min([
            amount,
            self.inventory.space_for(),
            afford_to_buy
        ])

        # Do the transaction - remove from shop, add to inventory, reduce gold
        bought_items = slot.remove_items(amount_to_buy)
        self.inventory.add_to(bought_items)
        self.inventory.gold_pouch.remove_gold(amount_to_buy * cost_of_item)

        self.status_bar_signal.emit("")
