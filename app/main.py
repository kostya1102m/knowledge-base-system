import sys
from PyQt6.QtWidgets import QApplication

from models import init_db, get_session, seed_demo_data
from views.role_selector import RoleSelectorView
from views.editor.editor import EditorWindow
from views.solver.solver import SolverWindow


class Application:

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        init_db()
        self.session = next(get_session())
        seed_demo_data(self.session)

        self.role_view = None
        self.editor = None
        self.solver = None

    def run(self):
        self.show_role_selector()
        sys.exit(self.app.exec())

    def show_role_selector(self):
        if self.editor:
            self.editor.close()
            self.editor = None
        if self.solver:
            self.solver.close()
            self.solver = None

        self.role_view = RoleSelectorView()
        self.role_view.role_selected.connect(self._on_role)
        self.role_view.show()

    def _on_role(self, role: str):
        self.role_view.close()
        self.role_view = None
        if role == 'expert':
            self._show_editor()
        else:
            self._show_solver()

    def _show_editor(self):
        self.session.expire_all()
        self.editor = EditorWindow(self.session)
        self.editor.go_back.connect(self.show_role_selector)
        self.editor.show()

    def _show_solver(self):
        self.session.expire_all()
        self.solver = SolverWindow(self.session)
        self.solver.go_back.connect(self.show_role_selector)
        self.solver.show()


if __name__ == "__main__":
    Application().run()