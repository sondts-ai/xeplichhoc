import sys
import random
import copy
import traceback
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QLabel, QSpinBox, QHBoxLayout, QLineEdit, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt

# ==========================
days = ["T2", "T3", "T4", "T5", "T6", "T7"]
cas = ["Ca 1", "Ca 2", "Ca 3", "Ca 4"]   # 4 ca

def init_empty_schedule():
    """Trả về dict với tất cả slot có list rỗng: (day,ca) -> []"""
    return {(d, c) for d in days for c in cas}

# ==========================
def expand_subjects(subjects):
    """Biến (môn, số buổi) thành danh sách (tên_buổi, ca_random)"""
    expanded = []
    for sub, count in subjects:
        for i in range(count):
            ca = random.choice(cas)  # tự chọn ca ngẫu nhiên
            expanded.append((f"{sub} ({i+1})", ca))
    return expanded

def random_schedule(subjects):
    expanded = expand_subjects(subjects)
    schedule = {(d, c): [] for d in days for c in cas}
    for name, ca in expanded:
        day = random.choice(days)
        slot = (day, ca)
        schedule[slot].append(name)
    return schedule

def evaluate(schedule):
    score = 0
    used_slots = [s for s, lst in schedule.items() if lst]
    score += len(used_slots) * 10

    day_count = {d: 0 for d in days}
    for (d, _), lst in schedule.items():
        day_count[d] += len(lst)

    for d in days:
        if day_count[d] == 0:
            score -= 5
        if day_count[d] > 4:
            score -= 5
    return score

def build_subj_to_slot(schedule):
    m = {}
    for slot, lst in schedule.items():
        for nm in lst:
            m[nm] = slot
    return m

def neighbor(schedule, subjects):
    expanded = expand_subjects(subjects)
    if len(expanded) < 2:
        return copy.deepcopy(schedule)

    new_schedule = {slot: list(lst) for slot, lst in schedule.items()}
    subj_to_slot = build_subj_to_slot(new_schedule)

    s1, s2 = random.sample(expanded, 2)
    name1, ca1 = s1
    name2, ca2 = s2

    slot1 = subj_to_slot.get(name1)
    slot2 = subj_to_slot.get(name2)

    if slot1 and slot2 and ca1 == ca2 and slot1 != slot2:
        new_schedule[slot1].remove(name1)
        new_schedule[slot2].remove(name2)
        new_schedule[slot1].append(name2)
        new_schedule[slot2].append(name1)
    else:
        rand_day = random.choice(days)
        new_slot = (rand_day, ca1)
        if slot1:
            new_schedule[slot1].remove(name1)
        new_schedule[new_slot].append(name1)
    return new_schedule

def hill_climbing(subjects, iterations=1000):
    current = random_schedule(subjects)
    best = copy.deepcopy(current)
    for _ in range(iterations):
        nxt = neighbor(current, subjects)
        if evaluate(nxt) >= evaluate(current):
            current = nxt
        if evaluate(current) > evaluate(best):
            best = copy.deepcopy(current)
    return best

def random_restart_hill_climbing(subjects, restarts=10, iterations=1000):
    best_overall = None
    for _ in range(restarts):
        candidate = hill_climbing(subjects, iterations)
        if best_overall is None or evaluate(candidate) > evaluate(best_overall):
            best_overall = candidate
    return best_overall

# ==========================
class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📅 Tối ưu Lịch Học - Không chọn ca")
        self.setGeometry(200, 200, 1000, 520)

        self.subjects = []

        self.label = QLabel("Nhập môn học + số buổi, sau đó nhấn nút để sinh lịch", self)

        self.table = QTableWidget(self)
        self.table.setRowCount(len(cas))
        self.table.setColumnCount(len(days))
        self.table.setHorizontalHeaderLabels(days)
        self.table.setVerticalHeaderLabels(cas)
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.subject_input = QLineEdit(self)
        self.subject_input.setPlaceholderText("Nhập tên môn học...")

        self.count_input = QSpinBox(self)
        self.count_input.setRange(1, 30)
        self.count_input.setValue(1)

        self.add_button = QPushButton("➕ Thêm môn", self)
        self.add_button.clicked.connect(self.add_subject)

        self.subject_list = QListWidget(self)

        self.iter_label = QLabel("Số lần lặp:", self)
        self.iter_input = QSpinBox(self)
        self.iter_input.setRange(100, 20000)
        self.iter_input.setValue(2000)

        self.restart_label = QLabel("Số lần restart:", self)
        self.restart_input = QSpinBox(self)
        self.restart_input.setRange(1, 200)
        self.restart_input.setValue(20)

        self.button = QPushButton("🔄 Sinh lịch tối ưu", self)
        self.button.clicked.connect(self.generate_schedule)

        self.clear_button = QPushButton("🗑️ Xóa tất cả", self)
        self.clear_button.clicked.connect(self.clear_all)

        h_sub_layout = QHBoxLayout()
        h_sub_layout.addWidget(self.subject_input)
        h_sub_layout.addWidget(QLabel("Số buổi:"))
        h_sub_layout.addWidget(self.count_input)
        h_sub_layout.addWidget(self.add_button)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.iter_label)
        h_layout.addWidget(self.iter_input)
        h_layout.addWidget(self.restart_label)
        h_layout.addWidget(self.restart_input)

        h_button_layout = QHBoxLayout()
        h_button_layout.addWidget(self.button)
        h_button_layout.addWidget(self.clear_button)
        h_button_layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(h_sub_layout)
        layout.addWidget(QLabel("Danh sách môn học đã nhập:"))
        layout.addWidget(self.subject_list)
        layout.addLayout(h_layout)
        layout.addWidget(self.table)
        layout.addLayout(h_button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_subject(self):
        subject = self.subject_input.text().strip()
        count = self.count_input.value()

        if subject:
            self.subjects.append((subject, count))
            self.subject_list.addItem(f"{subject} - {count} buổi")
            self.subject_input.clear()
            self.count_input.setValue(1)

    def clear_all(self):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa tất cả môn và lịch?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.subjects = []
            self.subject_list.clear()
            self.table.clearContents()
            self.label.setText("Nhập môn học + số buổi, sau đó nhấn nút để sinh lịch")

    def generate_schedule(self):
        if not self.subjects:
            self.label.setText("⚠️ Bạn chưa nhập môn học nào!")
            return

        iterations = self.iter_input.value()
        restarts = self.restart_input.value()

        try:
            best_schedule = random_restart_hill_climbing(self.subjects, restarts, iterations)

            self.table.clearContents()

            for r, ca in enumerate(cas):
                for c, d in enumerate(days):
                    cell_list = best_schedule.get((d, ca), [])
                    text = "\n".join(cell_list) if cell_list else ""
                    item = QTableWidgetItem(text)
                    item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
                    self.table.setItem(r, c, item)

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

            self.label.setText(f"🎯 Điểm đánh giá: {evaluate(best_schedule)}")
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            self.label.setText(f"❌ Lỗi khi sinh lịch: {e}. Xem console để biết chi tiết.")

# ==========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec_())
