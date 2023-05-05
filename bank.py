from PyQt5.QtGui import QPixmap
from items import concrete_types
from utilities import generate_label
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QAction


class BankSlot(QWidget):
    # Represents a slot in the bank's 10 x 10 item grid (one slot out of the 100 slots) - very similar code to ShopSlot
    # BankSlot is a wrapper around a collection of instantiated items, all the same type, stored in the bank
    # If there are no items in the collection, it's effectively an empty slot placeholder and has no visual display
    # BankSlot's alternative between empty placeholder and item collections as we add/remove items to/from the bank

    slot_clicked = pyqtSignal(int, type)  # number to withdraw x type of item withdrawing

    def __init__(self, slot_width, slot_height, status_bar_signal):
        # Bank slots are always initialized empty

        super().__init__()

        self.slot_width = slot_width
        self.slot_height = slot_height

        self.status_bar_signal = status_bar_signal

        self.setFixedSize(QSize(self.slot_width, self.slot_height))

        # `self.items` and `self.item_type` either:
        # - an empty list and None if no items being stored here: empty placeholder
        # - a list of the item instances and the concrete type of item objects in the list (guaranteed to all be same)
        self.items = []
        self.item_type = None

        # A bank slot is visually represented by the item's image, with the title and how many are stored below
        slot_layout = QVBoxLayout()

        self.item_image = QLabel("")
        self.text_label = generate_label("", 10)

        slot_layout.addWidget(self.item_image)
        slot_layout.addWidget(self.text_label)

        self.setLayout(slot_layout)

        # Create the withdrawing QActions in advance, to be used on left and right clicks for withdrawing from bank

        self.withdraw_one_action = QAction("Withdraw 1", self)
        self.withdraw_one_action.triggered.connect(self.withdraw_one_clicked)

        self.withdraw_five_action = QAction("Withdraw 5", self)
        self.withdraw_five_action.triggered.connect(self.withdraw_five_clicked)

        self.withdraw_ten_action = QAction("Withdraw 10", self)
        self.withdraw_ten_action.triggered.connect(self.withdraw_ten_clicked)

        self.withdraw_all_action = QAction("Withdraw all", self)
        self.withdraw_all_action.triggered.connect(self.withdraw_all_clicked)

    def update_text_label(self):
        # Update QLabel visually representing the item's title and the number of items stored in bank
        # Need to update whenever:
        # - all items of the type removed, so now it's an empty placeholder
        # - some items added so it's no longer empty: set to the title and how many now in bank
        # - some more items were added and it was non-empty to begin with: update how many in bank

        if len(self.items) == 0:
            # Empty, remove text
            self.text_label.setText("")

        else:
            # Not empty, so include text: item title x amount in bank
            self.text_label.setText("%s x %s" % (self.item_type.title, len(self.items)))

    def update_item_image(self):
        # Only call this method when we want to change the image, i.e.
        # empty -> non-empty (so add image): when adding items
        # non-empty -> empty (so remove image): when removing items

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
        # Is the slot not storing any items i.e. is it an empty placeholder slot in bank

        return len(self.items) == 0

    def add_items(self, new_items):
        # Add items to the bank slot, whether it was empty before or not empty
        # If it was not empty, we assume (and check) all the items being added are the same type as those already stored

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
        # This function is called from Bank.withdraw_from(), and it will only request an amount that is never more
        # than what is in the bank slot.
        # This is because withdrawn_from() is emitted to when we right-click withdraw from a non-empty bank slot
        # and the options for withdrawing (e.g. withdraw 1, 5, etc.) are dynamically presented on a right-click,
        # based on how many is in the slot
        # (actual amount passed in is what was requested, but capped at inventory space if not space for full amount)

        assert 0 < amount <= len(self.items)
        assert len(self.items) > 0

        removed_items = self.items[:amount]
        self.items = self.items[amount:]

        if len(self.items) == 0:
            # If no more items, make sure to set item type of bank slot to None
            # Only update image if we removed it, otherwise it would be the same and creating new QPixmaps constantly
            self.item_type = None
            self.update_item_image()

        # Update text label in both cases: non-empty -> empty and non-empty -> non-empty
        self.update_text_label()

        return removed_items

    def contextMenuEvent(self, e):

        if len(self.items) > 0:
            # Only want to present right-click menu on bank slots that actually have items
            # Only add the actions we have the number of items for, e.g. don't add 'withdraw 10' if we only have 5 items

            self.status_bar_signal.emit("")

            context = QMenu(self)
            context.addAction(self.withdraw_one_action)

            if len(self.items) >= 5:
                context.addAction(self.withdraw_five_action)

            if len(self.items) >= 10:
                context.addAction(self.withdraw_ten_action)

            if len(self.items) >= 2:
                context.addAction(self.withdraw_all_action)

            context.exec_(e.globalPos())

    def mouseReleaseEvent(self, e):
        # If we left-click on a non-empty slot, withdraw a single one of the item

        self.status_bar_signal.emit("")

        if e.button() == Qt.LeftButton and len(self.items) > 0:
            self.withdraw_one_clicked()

        e.ignore()

    def withdraw_one_clicked(self):

        self.slot_clicked.emit(1, self.item_type)

    def withdraw_five_clicked(self):

        self.slot_clicked.emit(5, self.item_type)

    def withdraw_ten_clicked(self):

        self.slot_clicked.emit(10, self.item_type)

    def withdraw_all_clicked(self):

        self.slot_clicked.emit(len(self.items), self.item_type)


class Bank(QWidget):
    # A widget representing the bank interface, that will replace the main game map display when opened
    # It is opened by clicking on a bank chest tile in the game (if player is within 1 tile of it)
    # There is one bank instance for the game, so different bank tiles interface to the same bank storage object `Bank`
    # The bank is represented as a 10x10 grid, with each slot a BankSlot object, that is either an empty placeholder,
    # or wraps a collection of non-zero items of the same type being stored
    # There is guaranteed to be only one bank slot for each item type

    def __init__(self, inventory, status_bar_signal):

        super().__init__()

        self.total_width = 1300
        self.total_height = 850

        self.inventory = inventory
        self.status_bar_signal = status_bar_signal

        self.setFixedSize(QSize(self.total_width, self.total_height))

        self.text_height = 50

        self.grid_height = self.total_height - self.text_height

        self.rows = 10
        self.cols = 10
        self.bank_limit = self.rows * self.cols

        self.slot_width = int(self.total_width/self.cols)
        self.slot_height = int(self.grid_height/self.rows)

        self.bank = QGridLayout()
        self.bank.setContentsMargins(10, 10, 10, 10)
        self.bank.setSpacing(2)

        # Fill all the grid slots with empty BankSlot's
        for i in range(self.bank_limit):

            col, row = i % 10, int(i/10)
            empty_bank_slot = BankSlot(self.slot_width, self.slot_height, self.status_bar_signal)
            empty_bank_slot.slot_clicked.connect(self.withdraw_from)
            self.bank.addWidget(empty_bank_slot, row, col)

        # Put bold 'BANK', a sort button, a deposit all button, and a close button above grid layout

        overall_layout = QVBoxLayout()
        overall_layout.setContentsMargins(5, 5, 5, 5)
        overall_layout.setSpacing(1)

        top_layout = QHBoxLayout()

        self.close_button = QPushButton("close")
        self.close_button.setFixedSize(QSize(100, self.text_height))

        self.sort_button = QPushButton("sort")
        self.sort_button.setFixedSize(QSize(100, self.text_height))
        self.sort_button.pressed.connect(self.sort)

        self.deposit_all_button = QPushButton("deposit all")
        self.deposit_all_button.setFixedSize(QSize(100, self.text_height))
        self.deposit_all_button.pressed.connect(self.inventory.deposit_all)

        top_layout.addWidget(self.sort_button)
        top_layout.addWidget(self.deposit_all_button)
        top_layout.addWidget(generate_label("BANK", 30, w=800, h=self.text_height))
        top_layout.addWidget(self.close_button)

        overall_layout.addLayout(top_layout)
        overall_layout.addLayout(self.bank)

        self.setLayout(overall_layout)

    def sort(self):
        # Sort the bank, so we re-order all the widgets based on the ordering defined in `items.concrete_types`
        # This will sort items into tools, then logs, then ores, etc. etc.
        # All empty bank slots go at the end
        # This function is the slot for the signal emitted when 'sort' button is pressed

        # Go through all bank slots, remove from grid, and split into two lists: slots with items and empty slots
        empty_widgets = []
        non_empty_widgets = []

        for i in range(self.bank_limit):

            col, row = i % 10, int(i/10)

            grid_item = self.bank.itemAtPosition(row, col)
            grid_slot = grid_item.widget()

            if len(grid_slot.items) == 0:
                empty_widgets.append(grid_slot)
            else:
                non_empty_widgets.append(grid_slot)

            self.bank.removeItem(grid_item)

        # Sort the slots containing items into their predefined order defined by `concrete_types`, e.g. tools first
        non_empty_widgets = sorted(non_empty_widgets, key=lambda x: concrete_types.index(x.item_type))

        # Add empty widgets back to the end of the list, so total list is length of all bank slots (10 x 10)
        sorted_widgets = non_empty_widgets + empty_widgets

        assert len(sorted_widgets) == self.bank_limit

        # Add back to grid: sorted items first, then fill with remainder of empty slots after
        for i in range(self.bank_limit):

            col, row = i % 10, int(i/10)
            self.bank.addWidget(sorted_widgets[i], row, col)

    def find_item_type_slot(self, item_type):
        # Searches all the slots to see if we have items of the type we are looking for stored in a slot
        # Will only ever pass in concrete types, not abstract types, so check types equal, not isinstance()
        # E.g. we will never find an generic 'Axe' type, only ever concrete 'Copper Axe' types
        # There will only ever be one slot for a given item type, so we return the first slot we find
        # Returns None if there is not a slot holding items of this type

        for i in range(self.bank_limit):

            col, row = i % 10, int(i/10)
            slot = self.bank.itemAtPosition(row, col).widget()

            if slot.item_type == item_type:
                return slot

        return None

    def find_first_empty_slot(self):
        # Searches the slots row by row until we find the first empty one (i.e. one with no items)
        # If there is no empty slot in the grid, return None

        for i in range(self.bank_limit):

            col, row = i % 10, int(i/10)
            slot = self.bank.itemAtPosition(row, col).widget()

            if len(slot.items) == 0:
                return slot

        return None

    def space_for(self, item_type):
        # There is space for an item type if either:
        # 1) there is already a slot in the grid holding this item type, in which case we can extend the items there
        # 2) if not, then there is at least one empty slot, where we can convert to a non-empty slot holding the items
        # Just because each slot in the bank has items in it, does not mean it's full
        # It's only full if there are no items of this type already where we can add to, *and* there are no empty slots
        # That's why `space_for` is parameterized by an item type

        if self.find_item_type_slot(item_type) is not None:
            return True

        if self.find_first_empty_slot() is not None:
            return True

        return False

    def deposit_to(self, items_to_deposit):
        # Takes a non-empty list of items, and adds to the bank's grid
        # - If already items of the same type in bank, add to that slot
        # - Otherwise, add to the first empty slot
        # We assume in this function we can deposit the items, i.e. there is space_for() the item types

        # Check there is at least one item to deposit, all the items are concrete item types
        assert len(items_to_deposit) > 0
        assert all(type(x) in concrete_types for x in items_to_deposit)

        # Get item type of items we're trying to deposit; check they're all the same type and there is a space for them
        item_type_to_deposit = type(items_to_deposit[0])

        assert all(type(items_to_deposit[i]) == item_type_to_deposit for i in range(len(items_to_deposit)))
        assert self.space_for(item_type_to_deposit)

        # Search all the slots to see if we already have a slot for items of this type
        slot = self.find_item_type_slot(item_type_to_deposit)

        if slot is None:
            # Need to make a new item type slot in grid - find the first empty slot, and add there
            # Guaranteed to be one as we checked for the space for above
            empty_slot = self.find_first_empty_slot()
            empty_slot.add_items(items_to_deposit)

        else:
            # We already have a bank slot for it, just add items to the slot
            slot.add_items(items_to_deposit)

    def withdraw_from(self, amount, item_type_to_withdraw):
        # Item type guaranteed to already be in bank because we will have right-clicked on it and emitted to this slot
        # The amount won't be more than what is in the bank
        # (but could be more than we have space for in inventory - so cap at that)

        if self.inventory.is_full():
            self.status_bar_signal.emit("Inventory full - cannot withdraw any items")
            return

        slot = self.find_item_type_slot(item_type_to_withdraw)
        assert slot is not None

        # We only want to withdraw exactly the amount we can manage, which depends on two factors
        # - the amount we actually requested - this amount is guaranteed to be in bank because only way withdraw_from()
        #   is called is by emitting from a bank slot right click, and the right click options dynamically show up
        #   depending on amount of items there is, e.g. won't offer "Withdraw 5" if only 4 items in stock
        # - the space in our inventory
        amount_to_withdraw = min([
            amount,
            self.inventory.space_for()
        ])

        # Do the transaction - remove from bank, add to inventory
        withdrawn_items = slot.remove_items(amount_to_withdraw)
        self.inventory.add_to(withdrawn_items)

        self.status_bar_signal.emit("")
