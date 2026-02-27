from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class RoleSelectorView(QWidget):

    role_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система классификации китообразных")
        self.setFixedSize(520, 350)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("Система классификации\nкитообразных")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont(); f.setPointSize(18); f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        sub = QLabel("Выберите режим работы:")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sf = QFont(); sf.setPointSize(12)
        sub.setFont(sf)
        layout.addWidget(sub)

        layout.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)

        btn_expert = QPushButton("Эксперт\n(Редактор базы знаний)")
        btn_expert.setFixedSize(200, 80)
        btn_expert.setStyleSheet(
            "QPushButton{background:#2196F3;color:white;border-radius:10px;font-size:11px}"
            "QPushButton:hover{background:#1976D2}"
        )
        btn_expert.clicked.connect(lambda: self.role_selected.emit('expert'))
        btn_row.addWidget(btn_expert)

        btn_user = QPushButton("Пользователь\n(Решатель задач)")
        btn_user.setFixedSize(200, 80)
        btn_user.setStyleSheet(
            "QPushButton{background:#4CAF50;color:white;border-radius:10px;font-size:11px}"
            "QPushButton:hover{background:#388E3C}"
        )
        btn_user.clicked.connect(lambda: self.role_selected.emit('user'))
        btn_row.addWidget(btn_user)

        layout.addLayout(btn_row)
        layout.addStretch()

        footer = QLabel("Классификация видов китообразных")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color:gray;font-size:10px;")
        layout.addWidget(footer)