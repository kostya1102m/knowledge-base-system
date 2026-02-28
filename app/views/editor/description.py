from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QCheckBox, QScrollArea, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from controllers.species import SpeciesController
from controllers.property import PropertyController
from controllers.description import DescriptionController


class DescriptionTab(QWidget):

    def __init__(self, species_ctrl: SpeciesController,
                 prop_ctrl: PropertyController,
                 desc_ctrl: DescriptionController):
        super().__init__()
        self.species_ctrl = species_ctrl
        self.prop_ctrl = prop_ctrl
        self.desc_ctrl = desc_ctrl
        self._species_data = []
        self._checkboxes = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        lbl = QLabel("Описание свойств вида")
        lbl.setFont(QFont("Trebuchet MS", 12, QFont.Weight.Bold))
        layout.addWidget(lbl)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.addWidget(QLabel("Виды:"))
        self.species_list = QListWidget()
        self.species_list.currentRowChanged.connect(self._on_species_changed)
        ll.addWidget(self.species_list)
        splitter.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Свойства:"))
        hdr.addStretch()

        btn_all = QPushButton("Выбрать все")
        btn_all.clicked.connect(self._select_all)
        hdr.addWidget(btn_all)

        btn_none = QPushButton("Снять все")
        btn_none.clicked.connect(self._clear_all)
        hdr.addWidget(btn_none)

        rl.addLayout(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.cb_container = QWidget()
        self.cb_layout = QVBoxLayout(self.cb_container)
        self.cb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.cb_container)
        rl.addWidget(scroll)

        splitter.addWidget(right)
        splitter.setSizes([300, 400])
        layout.addWidget(splitter)

    def refresh(self):
        self.species_list.clear()
        self._species_data = self.species_ctrl.get_all()
        for s in self._species_data:
            self.species_list.addItem(s.name)
        self._clear_cb_layout()

    def _on_species_changed(self, row):
        self._clear_cb_layout()
        if row < 0 or row >= len(self._species_data):
            return

        species = self._species_data[row]
        described_ids = {p.id for p in self.desc_ctrl.get_described_properties(species.id)}

        self._checkboxes = []
        for prop in self.prop_ctrl.get_all():
            cb = QCheckBox(prop.name)
            cb.setChecked(prop.id in described_ids)
            cb.stateChanged.connect(
                lambda state, sid=species.id, pid=prop.id:
                    self.desc_ctrl.set_property(sid, pid, state == 2)
            )
            self.cb_layout.addWidget(cb)
            self._checkboxes.append(cb)

    def _select_all(self):
        for cb in self._checkboxes:
            cb.setChecked(True)

    def _clear_all(self):
        for cb in self._checkboxes:
            cb.setChecked(False)

    def _clear_cb_layout(self):
        while self.cb_layout.count():
            child = self.cb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._checkboxes = []