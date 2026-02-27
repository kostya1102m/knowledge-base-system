from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from controllers.species import SpeciesController
from controllers.property import PropertyController
from controllers.value import ValueController
from controllers.description import DescriptionController
from controllers.assignment import AssignmentController


class AssignmentTab(QWidget):

    def __init__(self, species_ctrl: SpeciesController,
                 prop_ctrl: PropertyController,
                 val_ctrl: ValueController,
                 desc_ctrl: DescriptionController,
                 assign_ctrl: AssignmentController):
        super().__init__()
        self.species_ctrl = species_ctrl
        self.prop_ctrl = prop_ctrl
        self.val_ctrl = val_ctrl
        self.desc_ctrl = desc_ctrl
        self.assign_ctrl = assign_ctrl
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        lbl = QLabel("Значения свойств для вида кита")
        lbl.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(lbl)

        row = QHBoxLayout()

        row.addWidget(QLabel("Вид:"))
        self.species_combo = QComboBox()
        self.species_combo.setMinimumWidth(250)
        self.species_combo.currentIndexChanged.connect(self._on_species_changed)
        row.addWidget(self.species_combo)

        row.addWidget(QLabel("Свойство:"))
        self.prop_combo = QComboBox()
        self.prop_combo.setMinimumWidth(250)
        self.prop_combo.currentIndexChanged.connect(self._on_property_changed)
        row.addWidget(self.prop_combo)

        row.addStretch()
        layout.addLayout(row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.cb_container = QWidget()
        self.cb_layout = QVBoxLayout(self.cb_container)
        self.cb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.cb_container)
        layout.addWidget(scroll)

    def refresh(self):
        self.species_combo.blockSignals(True)
        cur_sp = self.species_combo.currentData()
        self.species_combo.clear()
        for s in self.species_ctrl.get_all():
            self.species_combo.addItem(s.name, s.id)
        if cur_sp is not None:
            idx = self.species_combo.findData(cur_sp)
            if idx >= 0:
                self.species_combo.setCurrentIndex(idx)
        self.species_combo.blockSignals(False)
        self._on_species_changed()

    def _on_species_changed(self, _=None):
        self.prop_combo.blockSignals(True)
        cur_pr = self.prop_combo.currentData()
        self.prop_combo.clear()

        sid = self.species_combo.currentData()
        if sid is not None:
            for p in self.desc_ctrl.get_described_properties(sid):
                self.prop_combo.addItem(p.name, p.id)

        if cur_pr is not None:
            idx = self.prop_combo.findData(cur_pr)
            if idx >= 0:
                self.prop_combo.setCurrentIndex(idx)

        self.prop_combo.blockSignals(False)
        self._on_property_changed()

    def _on_property_changed(self, _=None):
        self._clear_layout()

        sid = self.species_combo.currentData()
        pid = self.prop_combo.currentData()
        if sid is None or pid is None:
            return

        assigned_ids = {v.id for v in self.assign_ctrl.get_values(sid, pid)}

        for val in self.val_ctrl.get_for_property(pid):
            cb = QCheckBox(val.name)
            cb.setChecked(val.id in assigned_ids)
            cb.stateChanged.connect(
                lambda state, s=sid, p=pid, v=val.id:
                    self.assign_ctrl.set_value(s, p, v, state == 2)
            )
            self.cb_layout.addWidget(cb)

    def _clear_layout(self):
        while self.cb_layout.count():
            child = self.cb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()