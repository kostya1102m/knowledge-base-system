from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QLabel,
    QComboBox, QMessageBox
)
from PyQt6.QtGui import QFont
from controllers.property import PropertyController
from controllers.value import ValueController


class ValuesTab(QWidget):

    def __init__(self, prop_ctrl: PropertyController, val_ctrl: ValueController):
        super().__init__()
        self.prop_ctrl = prop_ctrl
        self.val_ctrl = val_ctrl
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        lbl = QLabel("Управление возможными значениями свойств")
        lbl.setFont(QFont("Trebuchet MS", 12, QFont.Weight.Bold))
        layout.addWidget(lbl)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Свойство:"))
        self.combo = QComboBox()
        self.combo.setMinimumWidth(250)
        self.combo.currentIndexChanged.connect(self._refresh_values)
        row1.addWidget(self.combo)
        row1.addStretch()
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите название значения...")
        self.input.returnPressed.connect(self._add)
        row2.addWidget(self.input)

        btn = QPushButton("Добавить")
        btn.setStyleSheet("background:#4CAF50;color:white;padding:6px 16px;border-radius:4px;")
        btn.clicked.connect(self._add)
        row2.addWidget(btn)
        layout.addLayout(row2)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

    def refresh(self):
        self.combo.blockSignals(True)
        cur = self.combo.currentData()
        self.combo.clear()
        for p in self.prop_ctrl.get_all():
            self.combo.addItem(p.name, p.id)
        if cur is not None:
            idx = self.combo.findData(cur)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)
        self.combo.blockSignals(False)
        self._refresh_values()

    def _refresh_values(self):
        self.list_widget.clear()
        pid = self.combo.currentData()
        if pid is None:
            return
        for v in self.val_ctrl.get_for_property(pid):
            item = QListWidgetItem()
            w = self._item_widget(v.name, lambda _, vid=v.id: self._delete(vid))
            item.setSizeHint(w.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, w)

    def _add(self):
        pid = self.combo.currentData()
        if pid is None:
            QMessageBox.warning(self, "Ошибка", "Выберите свойство.")
            return
        name = self.input.text().strip()
        if not name:
            return
        if self.val_ctrl.add(pid, name) is None:
            QMessageBox.warning(self, "Ошибка", f"Значение «{name}» уже существует.")
            return
        self.input.clear()
        self._refresh_values()

    def _delete(self, vid: int):
        reply = QMessageBox.question(
            self, "Подтверждение", "Удалить значение?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.val_ctrl.remove(vid)
            self._refresh_values()

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