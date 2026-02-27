from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
from PyQt6.QtCore import pyqtSignal
from sqlalchemy.orm import Session

from controllers import (
    SpeciesController, PropertyController, ValueController,
    DescriptionController, AssignmentController, CompletenessController
)
from views.editor.species import SpeciesTab
from views.editor.properties import PropertiesTab
from views.editor.values import ValuesTab
from views.editor.description import DescriptionTab
from views.editor.assignment import AssignmentTab
from views.editor.completeness import CompletenessTab


class EditorWindow(QMainWindow):

    go_back = pyqtSignal()

    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.setWindowTitle("Редактор базы знаний — Классификация китообразных")
        self.setMinimumSize(900, 600)

        self.species_ctrl = SpeciesController(session)
        self.property_ctrl = PropertyController(session)
        self.value_ctrl = ValueController(session)
        self.desc_ctrl = DescriptionController(session)
        self.assign_ctrl = AssignmentController(session)
        self.completeness_ctrl = CompletenessController(session)

        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        top = QHBoxLayout()
        btn = QPushButton("← Назад к выбору роли")
        btn.setFixedWidth(200)
        btn.clicked.connect(self.go_back.emit)
        top.addWidget(btn)
        top.addStretch()
        layout.addLayout(top)

        self.tabs = QTabWidget()

        self.species = SpeciesTab(self.species_ctrl)
        self.properties = PropertiesTab(self.property_ctrl)
        self.values = ValuesTab(self.property_ctrl, self.value_ctrl)
        self.description = DescriptionTab(
            self.species_ctrl, self.property_ctrl, self.desc_ctrl
        )
        self.assignment = AssignmentTab(
            self.species_ctrl, self.property_ctrl,
            self.value_ctrl, self.desc_ctrl, self.assign_ctrl
        )
        self.completeness = CompletenessTab(self.completeness_ctrl)

        self.tabs.addTab(self.species, "Виды китов")
        self.tabs.addTab(self.properties, "Свойства")
        self.tabs.addTab(self.values, "Возможные значения")
        self.tabs.addTab(self.description, "Описания свойств вида")
        self.tabs.addTab(self.assignment, "Значения для вида")
        self.tabs.addTab(self.completeness, "Проверка полноты")

        self.tabs.currentChanged.connect(self._on_changed)
        layout.addWidget(self.tabs)

    def _on_changed(self, index: int):
        self.session.expire_all()
        tab = self.tabs.widget(index)
        if hasattr(tab, 'refresh'):
            tab.refresh()