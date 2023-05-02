from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLabel


def generate_label(text, font_size, alignment=Qt.AlignCenter, w=None, h=None):

    label = QLabel(text)

    font = label.font()
    font.setPointSize(font_size)
    label.setFont(font)

    label.setAlignment(alignment)

    if w is not None and h is not None:
        label.setFixedSize(QSize(w, h))

    return label
