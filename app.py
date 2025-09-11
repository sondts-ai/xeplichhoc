import streamlit as st
import random
import copy
import pandas as pd

# ==========================
days = ["T2", "T3", "T4", "T5", "T6", "T7"]
cas = ["Ca 1", "Ca 2", "Ca 3", "Ca 4"]   # 4 ca
MAX_SLOTS = len(days) * len(cas)  # 24 slot

def expand_subjects(subjects):
    expanded = []
    for sub, count in subjects:
        for i in range(count):
            ca = random.choice(cas)
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
    day_count = {d: 0 for d in days}
    ca_count = {c: 0 for c in cas}
    subj_days = {}

    for (d, c), lst in schedule.items():
        day_count[d] += len(lst)
        ca_count[c] += len(lst)
        for name in lst:
            subj = name.split(" ")[0]
            subj_days.setdefault(subj, []).append(d)

    # 1. Mỗi ngày có ít nhất 1 buổi
    for d in days:
        if day_count[d] > 0:
            score += 10
        else:
            score -= 10

    # 2. Phạt nếu ngày >4 buổi
    for d in days:
        if day_count[d] > 4:
            score -= (day_count[d] - 4) * 5

    # 3. Cân bằng ca
    avg = sum(ca_count.values()) / len(cas)
    variance = sum((c - avg) ** 2 for c in ca_count.values())
    score -= variance * 0.5

    # 4. Tránh dồn môn vào cùng slot
    for (d, c), lst in schedule.items():
        if len(lst) > 1:
            score -= (len(lst) - 1) * 3

    # 5. Trải đều môn
    for subj, ds in subj_days.items():
        unique_days = len(set(ds))
        if unique_days < len(ds):
            score -= (len(ds) - unique_days) * 5

    # 6. Tránh học cùng môn 2 ngày liên tiếp
    day_index = {d: i for i, d in enumerate(days)}
    for subj, ds in subj_days.items():
        idxs = sorted(day_index[d] for d in ds)
        for i in range(1, len(idxs)):
            if idxs[i] - idxs[i-1] == 1:
                score -= 2

    # 7. Phạt ngày học kín 4 ca
    for d in days:
        if day_count[d] == len(cas):
            score -= 8

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
st.title("📅 Tối ưu Lịch Học (Streamlit)")
st.write("Nhập môn học và số buổi, sau đó nhấn nút để sinh lịch tối ưu.")

# State lưu môn học
if "subjects" not in st.session_state:
    st.session_state.subjects = []

col1, col2 = st.columns([3, 1])
with col1:
    subject = st.text_input("Tên môn học")
with col2:
    count = st.number_input("Số buổi", min_value=1, max_value=30, value=1, step=1)

if st.button("➕ Thêm môn"):
    total_sessions = sum(c for _, c in st.session_state.subjects)
    if total_sessions + count > MAX_SLOTS:
        st.warning(f"Tổng số buổi ({total_sessions + count}) vượt quá số slot ({MAX_SLOTS}).")
    else:
        st.session_state.subjects.append((subject, count))
        st.success(f"Đã thêm môn: {subject} ({count} buổi)")

if st.button("🗑️ Xóa tất cả"):
    st.session_state.subjects = []

if st.session_state.subjects:
    st.write("### Danh sách môn học đã nhập")
    st.table(st.session_state.subjects)

iterations = st.number_input("Số lần lặp (iterations)", min_value=100, max_value=20000, value=2000, step=100)
restarts = st.number_input("Số lần restart", min_value=1, max_value=200, value=20, step=1)

if st.button("🔄 Sinh lịch tối ưu"):
    if not st.session_state.subjects:
        st.warning("⚠️ Bạn chưa nhập môn học nào!")
    else:
        best_schedule = random_restart_hill_climbing(st.session_state.subjects, restarts, iterations)
        score = evaluate(best_schedule)
        st.success(f"🎯 Điểm đánh giá: {score}")

        # Tạo dataframe 4x6 (Ca 1-4 × T2-T7)
        data = []
        for ca in cas:
            row = []
            for d in days:
                cell_list = best_schedule.get((d, ca), [])
                text = "\n".join(cell_list) if cell_list else ""
                row.append(text)
            data.append(row)

        df = pd.DataFrame(data, index=cas, columns=days)

        st.write("### Lịch học tối ưu")
        st.dataframe(df, height=400, use_container_width=True)
