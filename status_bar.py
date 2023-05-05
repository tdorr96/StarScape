from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLabel


class StatusBar(QLabel):
    # Text widget for the text display underneath the main game's display widget
    # In most of the code we pass around a reference to a signal `status_bar_signal`
    # which when emitted on with a str will update the text of this bar

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

        self.setText(text)
