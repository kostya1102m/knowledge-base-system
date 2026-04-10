from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt6.QtGui import QFont
from controllers.completeness import CompletenessController


class CompletenessTab(QWidget):

    def __init__(self, ctrl: CompletenessController):
        super().__init__()
        self.ctrl = ctrl
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        lbl = QLabel("Проверка полноты базы знаний")
        lbl.setFont(QFont("Trebuchet MS", 12, QFont.Weight.Bold))
        layout.addWidget(lbl)

        btn = QPushButton("Проверить полноту")
        btn.setStyleSheet(
            "background:#FF9800;color:white;padding:8px 20px;"
            "border-radius:4px;font-size:13px;"
        )
        btn.clicked.connect(self._check)
        layout.addWidget(btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    def _check(self):
        errors = self.ctrl.check()
        self.output.clear()

        if not errors:
            self.output.setStyleSheet("color:green;font-size:13px;")
            self.output.setText(
                "База знаний полна.\n\n"
                "Все виды имеют описания свойств, все свойства имеют "
                "заданные значения, все значения корректны."
            )
        else:
            self.output.setStyleSheet("color:red;font-size:13px;")
            lines = ["Обнаружены проблемы:\n"]
            for i, e in enumerate(errors, 1):
                lines.append(f"{i}. {e}\n")
            self.output.setText("\n".join(lines))

    def refresh(self):
        self.output.clear()