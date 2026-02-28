from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QMessageBox
)
from PyQt6.QtGui import QFont
from controllers.property import PropertyController


class PropertiesTab(QWidget):

    def __init__(self, ctrl: PropertyController):
        super().__init__()
        self.ctrl = ctrl
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)

        lbl = QLabel("Управление свойствами (признаками)")
        lbl.setFont(QFont("Trebuchet MS", 12, QFont.Weight.Bold))
        layout.addWidget(lbl)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите название свойства...")
        self.input.returnPressed.connect(self._add)
        row.addWidget(self.input)

        btn = QPushButton("Добавить")
        btn.setStyleSheet("background:#4CAF50;color:white;padding:6px 16px;border-radius:4px;")
        btn.clicked.connect(self._add)
        row.addWidget(btn)
        layout.addLayout(row)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

    def _add(self):
        name = self.input.text().strip()
        if not name:
            return
        if self.ctrl.add(name) is None:
            QMessageBox.warning(self, "Ошибка", f"Свойство «{name}» уже существует.")
            return
        self.input.clear()
        self.refresh()

    def _delete(self, pid: int):
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить свойство и все связанные данные?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.ctrl.remove(pid)
            self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for p in self.ctrl.get_all():
            item = QListWidgetItem()
            w = self._item_widget(p.name, lambda _, pid=p.id: self._delete(pid))
            item.setSizeHint(w.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, w)

    def _item_widget(self, text, on_delete):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.addWidget(QLabel(text))
        lay.addStretch()
        btn = QPushButton("−")
        btn.setFixedSize(30, 30)
        btn.setStyleSheet(
            "QPushButton{background:#f44336;color:white;border-radius:15px;"
            "font-size:16px;font-weight:bold}"
            "QPushButton:hover{background:#d32f2f}"
        )
        btn.clicked.connect(on_delete)
        lay.addWidget(btn)
        return w