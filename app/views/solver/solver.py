from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QCheckBox, QTextEdit, QGroupBox,
    QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from sqlalchemy.orm import Session

from controllers import (
    PropertyController, ValueController, SolverController
)


class SolverWindow(QMainWindow):

    go_back = pyqtSignal()

    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.prop_ctrl = PropertyController(session)
        self.val_ctrl = ValueController(session)
        self.solver_ctrl = SolverController(session)
        self.property_checkboxes: dict[int, dict[int, QCheckBox]] = {}

        self.setWindowTitle("Решатель задач — Классификация китообразных")
        self.setMinimumSize(1000, 700)
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)

        top = QHBoxLayout()
        btn_back = QPushButton("← Назад к выбору роли")
        btn_back.setFixedWidth(50)
        btn_back.setFixedWidth(200)
        btn_back.clicked.connect(self.go_back.emit)
        top.addWidget(btn_back)
        top.addStretch()
        title = QLabel("🐋 Решатель задач — Определение вида кита")
        title.setFont(QFont("Trebuchet MS", 14, QFont.Weight.Bold))
        title.setFixedHeight(50)
        top.addWidget(title)
        top.addStretch()
        main.addLayout(top)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)

        ll.addWidget(self._bold_label("Введите наблюдаемые признаки:"))

        hint = QLabel(
            "Отметьте значения свойств, которые вы наблюдаете.\n"
            "Можно указать несколько значений для одного свойства.\n"
            "Не обязательно заполнять все свойства."
        )
        hint.setStyleSheet("color:gray;font-style:italic;")
        ll.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.input_container = QWidget()
        self.input_layout = QVBoxLayout(self.input_container)
        self.input_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.input_container)
        ll.addWidget(scroll)

        btns = QHBoxLayout()
        btn_solve = QPushButton("🔍 Определить вид")
        btn_solve.setFixedHeight(40)
        btn_solve.setStyleSheet(
            "QPushButton{background:#4CAF50;color:white;font-size:14px;"
            "font-weight:bold;border-radius:6px;padding:0 20px}"
            "QPushButton:hover{background:#388E3C}"
        )
        btn_solve.clicked.connect(self._solve)
        btns.addWidget(btn_solve)

        btn_clear = QPushButton("Очистить")
        btn_clear.setFixedHeight(40)
        btn_clear.setStyleSheet(
            "QPushButton{background:#9E9E9E;color:white;font-size:13px;"
            "border-radius:6px;padding:0 20px}"
            "QPushButton:hover{background:#757575}"
        )
        btn_clear.clicked.connect(self._clear)
        btns.addWidget(btn_clear)

        ll.addLayout(btns)
        splitter.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self._bold_label("Результат классификации:"))

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("font-size:12px;")
        rl.addWidget(self.result_output)

        splitter.addWidget(right)
        splitter.setSizes([450, 550])
        main.addWidget(splitter)

        self._load_properties()

    def _load_properties(self):
        self._clear_layout(self.input_layout)
        self.property_checkboxes = {}

        props = self.prop_ctrl.get_all()
        if not props:
            lbl = QLabel("База знаний пуста. Обратитесь к эксперту.")
            lbl.setStyleSheet("color:red;font-size:13px;")
            self.input_layout.addWidget(lbl)
            return

        for prop in props:
            group = QGroupBox(prop.name)
            group.setStyleSheet(
                "QGroupBox{font-weight:bold;font-size:12px;border:1px solid #ccc;"
                "border-radius:6px;margin-top:8px;padding-top:16px}"
                "QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px}"
            )
            gl = QVBoxLayout()
            self.property_checkboxes[prop.id] = {}

            values = self.val_ctrl.get_for_property(prop.id)
            for val in values:
                cb = QCheckBox(val.name)
                cb.setStyleSheet("font-weight:normal;")
                gl.addWidget(cb)
                self.property_checkboxes[prop.id][val.id] = cb

            if not values:
                no_lbl = QLabel("(нет возможных значений)")
                no_lbl.setStyleSheet("color:gray;font-style:italic;font-weight:normal;")
                gl.addWidget(no_lbl)

            group.setLayout(gl)
            self.input_layout.addWidget(group)

    def _clear(self):
        for cbs in self.property_checkboxes.values():
            for cb in cbs.values():
                cb.setChecked(False)
        self.result_output.clear()

    def _solve(self):
        user_input = {}
        has_any = False

        for pid, cbs in self.property_checkboxes.items():
            selected = [vid for vid, cb in cbs.items() if cb.isChecked()]
            if selected:
                user_input[pid] = selected
                has_any = True

        if not has_any:
            QMessageBox.information(
                self, "Нет данных",
                "Выберите хотя бы одно значение для классификации."
            )
            return

        result = self.solver_ctrl.solve(user_input)
        self._display(result)

    def _display(self, result: dict):
        self.result_output.clear()

        all_results = result['all_results']
        best_species = result['best_species']
        matched_count = result['matched_count']

        matched = [r for r in all_results if r['matched']]
        rejected = [r for r in all_results if not r['matched']]

        html = (
            "<style>"
            ".match{color:#2E7D32} .reject{color:#C62828} .neutral{color:#616161}"
            ".best{color:#1565C0} .name{font-size:15px;font-weight:bold}"
            ".detail{margin-left:20px;font-size:12px}"
            ".prob{font-size:11px;color:#555}"
            ".best-banner{background:#E3F2FD;border:2px solid #1565C0;"
            "border-radius:8px;padding:12px;margin:8px 0}"
            "hr{border:1px solid #eee}"
            "</style>"
        )

        html += "<h2>Результат определения</h2>"

        # ── Баннер ML-рекомендации ──
        if best_species and matched_count > 1:
            best_r = next((r for r in matched if r['is_best']), None)
            prob_pct = f"{best_r['probability'] * 100:.1f}%" if best_r else ""
            html += (
                f"<div class='best-banner'>"
                f"<p class='best'><b>🤖 ML-рекомендация:</b></p>"
                f"<p class='name best'>⭐ {best_species.name}</p>"
                f"<p class='prob'>Уверенность модели: {prob_pct}</p>"
                f"<p class='neutral' style='font-size:11px'>"
                f"Из {matched_count} подходящих видов модель считает этот наиболее вероятным."
                f"</p></div>"
            )
        elif best_species and matched_count == 1:
            best_r = next((r for r in matched if r['is_best']), None)
            prob_pct = f"{best_r['probability'] * 100:.1f}%" if best_r else ""
            html += (
                f"<div class='best-banner'>"
                f"<p class='match'><b>🎯 Единственный подходящий вид:</b></p>"
                f"<p class='name match'>⭐ {best_species.name}</p>"
                f"<p class='prob'>Уверенность модели: {prob_pct}</p>"
                f"</div>"
            )

        if matched:
            html += f"<p class='match'><b>✅ Подходящие виды ({len(matched)}):</b></p>"
            for r in matched:
                star = " ⭐" if r['is_best'] else ""
                prob_pct = f"{r['probability'] * 100:.1f}%"
                html += (
                    f"<p class='name match'>🐋 {r['species'].name}{star} "
                    f"<span class='prob'>({prob_pct})</span></p>"
                )
                html += self._fmt_details(r['details'])
                html += "<hr>"
        else:
            html += (
                "<p class='reject'><b>Ни один вид не соответствует.</b></p>"
                "<p class='neutral'>Измените данные или дополните базу знаний.</p><hr>"
            )


        if rejected:
            html += f"<p class='reject'><b>❌ Опровергнутые виды ({len(rejected)}):</b></p>"
            for r in rejected:
                prob_pct = f"{r['probability'] * 100:.1f}%"
                html += (
                    f"<p class='name reject'>✗ {r['species'].name} "
                    f"<span class='prob'>({prob_pct})</span></p>"
                )
                html += self._fmt_details(r['details'])
                html += "<hr>"

        self.result_output.setHtml(html)

    def _fmt_details(self, details):
        html = ""
        for d in details:
            pname = d['property'].name
            uv = ", ".join(v.name for v in d['user_values'])
            sv = ", ".join(v.name for v in d['species_values']) if d['species_values'] else "—"
            note = d.get('note', '')

            if d['match'] is None:
                html += (
                    f"<p class='detail neutral'>• <b>{pname}</b>: "
                    f"[{uv}] — <i>{note}</i></p>"
                )
            elif d['match']:
                html += (
                    f"<p class='detail match'>• <b>{pname}</b>: "
                    f"✓ совпадает (ваш: [{uv}], вид: [{sv}])</p>"
                )
            else:
                html += (
                    f"<p class='detail reject'>• <b>{pname}</b>: "
                    f"✗ не совпадает (ваш: [{uv}], вид: [{sv}])</p>"
                )
        return html

    def refresh_data(self):
        self.session.expire_all()
        self.solver_ctrl.retrain()
        self._load_properties()
        self.result_output.clear()

    def _bold_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Trebuchet MS", 12, QFont.Weight.Bold))
        return lbl

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()