from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QSpinBox, QTextEdit

from powerpoint_app.domain.teaching import TeachingProfile
from powerpoint_app.planning.teaching import load_profile, save_profile


class TeachingDialog(QDialog):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        self.setWindowTitle("Undervisningsprofil")
        self.resize(650, 650)
        existing = load_profile(root)
        data = existing.model_dump() if existing else {"audience": "Maskinmesterstuderende på 4. semester", "subject": "Teknisk matematik og fysik"}
        form = QFormLayout(self)
        self.fields = {}
        for key, title in [("subject", "Fag"), ("audience", "Målgruppe"), ("practical_context", "Praktisk sammenhæng"), ("required_method", "Krævet regnemetode")]:
            field = QLineEdit(data.get(key, "")); self.fields[key] = field; form.addRow(title, field)
        for key, title in [("learning_objectives", "Læringsmål (ét pr. linje)"), ("prior_knowledge", "Forkundskaber (én pr. linje)"), ("notation", "Notation der skal bevares")]:
            field = QTextEdit(); field.setPlainText("\n".join(data.get(key, []))); field.setMaximumHeight(90)
            self.fields[key] = field; form.addRow(title, field)
        self.support = QComboBox()
        for label, key in [("Nyt stof", "beginner"), ("Støttet øvelse", "guided"), ("Repetition", "revision")]: self.support.addItem(label, key)
        self.support.setCurrentIndex(self.support.findData(data.get("support", "guided")))
        form.addRow("Støtte", self.support)
        self.minutes = QSpinBox(); self.minutes.setRange(1, 600); self.minutes.setValue(data.get("duration_minutes", 15)); form.addRow("Minutter inkl. øvelser", self.minutes)
        self.count = QSpinBox(); self.count.setRange(1, 100); self.count.setValue(data.get("approximate_slides", 10)); form.addRow("Logiske slides før afsløringer", self.count)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save); buttons.rejected.connect(self.reject); form.addRow(buttons)

    def save(self):
        data = {key: [line.strip() for line in field.toPlainText().splitlines() if line.strip()] if isinstance(field, QTextEdit) else field.text().strip() for key, field in self.fields.items()}
        data.update(support=self.support.currentData(), duration_minutes=self.minutes.value(), approximate_slides=self.count.value())
        try:
            save_profile(self.root, TeachingProfile.model_validate(data))
        except ValueError as exc:
            QMessageBox.warning(self, "Profilen mangler oplysninger", str(exc)); return
        self.accept()
