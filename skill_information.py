from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
from utilities import generate_label
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton


class SkillInformation(QWidget):
    # A widget that displays when we click on a skill in the skills widget, one for each skill type
    # On clicking it will replace the main game display widget until we press the close button/press ESC

    def __init__(self, skill):
        # `skill` is a reference to a class type, a skill: Woodcutting, Mining, etc.
        # that has static class members that help us populate this class

        super().__init__()

        self.setFixedSize(QSize(1300, 850))

        overall_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        self.close_button = QPushButton("Close")
        self.close_button.setFixedSize(QSize(100, 50))

        top_layout.addWidget(generate_label(skill.title.upper(), 30, w=1000, h=50))
        top_layout.addWidget(self.close_button)

        overall_layout.addLayout(top_layout)

        overall_layout.addWidget(
            generate_label(skill.relevant_tools_type, 25, alignment=Qt.AlignLeft | Qt.AlignVCenter, w=1300, h=50)
        )

        for tool in skill.relevant_tools:

            tool_layout = QHBoxLayout()

            tool_image = QLabel("")
            tool_image.setPixmap(QPixmap(tool.path_to_icon).scaled(QSize(50, 50), Qt.KeepAspectRatio))
            tool_image.setAlignment(Qt.AlignCenter)

            tool_layout.addWidget(tool_image)
            tool_layout.addWidget(generate_label(tool.title, 15))
            tool_layout.addWidget(generate_label("Level %s" % tool.skill_level_required, 15))

            overall_layout.addLayout(tool_layout)

        overall_layout.addWidget(
            generate_label(skill.relevant_interactables_type, 25, alignment=Qt.AlignLeft | Qt.AlignVCenter, w=1300, h=50)
        )

        for interactable in skill.relevant_interactables:

            interactable_layout = QHBoxLayout()

            interactable_image = QLabel("")
            interactable_image.setPixmap(QPixmap(interactable.path_to_icon).scaled(QSize(50, 50), Qt.KeepAspectRatio))
            interactable_image.setAlignment(Qt.AlignCenter)

            interactable_layout.addWidget(interactable_image)
            interactable_layout.addWidget(generate_label(interactable.title, 15))
            interactable_layout.addWidget(generate_label(skill.relevant_interactables[interactable], 15))

            overall_layout.addLayout(interactable_layout)

        self.setLayout(overall_layout)
