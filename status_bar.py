from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLabel


class StatusBar(QLabel):
    # Label widget for the text display underneath the game map widget
    # Signal in Game object connects to this label to update whenever anything notable happens
    # Removes status string whenever we interact with the game and nothing notable happened, to remove previous status
    # E.g. if we update with "level gained", on the next chop if we don't gain a level remove the previous status
    # This is achieved by adding a signal.emit("") tto all entry points for interactions with the game (click/key press)

    def __init__(self):

        super().__init__()

        self.setFixedSize(QSize(1300, 50))

        self.setText("Welcome!")

        font = self.font()
        font.setPointSize(20)
        self.setFont(font)

        self.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)

    def update_status_bar(self, text):
        # Slot for signals emitted when status bar text needs to change
        # OR be reset to empty string

        self.setText(text)
