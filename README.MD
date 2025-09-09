# 📅 ScheduleApp - Tối ưu Lịch Học

Ứng dụng PyQt5 cho phép nhập danh sách môn học, số buổi mỗi môn và tự động sắp xếp lịch học tối ưu bằng **thuật toán Hill Climbing + Random Restart**.

---

## 🚀 Tính năng chính

* Nhập môn học và số buổi học.
* Tự động phân bổ vào các ngày (T2 - T7) và 4 ca học/ngày.
* Dùng **Hill Climbing** để tối ưu lịch, tránh xung đột và cân bằng lịch học.
* Hiển thị lịch trên bảng dạng **Table**.
* Cho phép xoá từng môn học đã nhập hoặc **xoá toàn bộ**.
* Điểm đánh giá lịch học hiển thị ngay sau khi sinh lịch.

---

## 🛠️ Công nghệ sử dụng

* Python 3
* PyQt5 (GUI)
* Random + Hill Climbing (thuật toán tối ưu)

---

## 📂 Cấu trúc file

```
ScheduleApp/
│-- app11.py # Code chính của ứng dụng
│-- requirements.txt # Thư viện cần cài
│-- README.md # Hướng dẫn sử dụng
```

---

## ▶️ Cách chạy

1. Cài đặt thư viện cần thiết:

   ```bash
    pip install -r requirements.txt
   ```

2. Chạy ứng dụng:

   ```bash
   python app11.py
   ```

3. Giao diện sẽ hiện ra:

   * Nhập tên môn học + số buổi.
   * Thêm môn vào danh sách.
   * Nhấn **🔄 Sinh lịch tối ưu** để tạo lịch.
   * Dùng **🗑️ Xoá tất cả** để xoá danh sách và bảng lịch.

---

## 📊 Thuật toán tối ưu

* **Hill Climbing**: tìm lịch tốt hơn bằng cách đổi chỗ buổi học.
* **Random Restart**: chạy nhiều lần Hill Climbing để tránh rơi vào cực trị địa phương.
* **Hàm đánh giá (Evaluate)**:

  * Điểm thưởng cho việc phân bổ đều.
  * Phạt nếu một ngày không có môn nào hoặc quá tải (>4 ca).

---

## 📌 Ghi chú

* Nếu nhập quá nhiều môn trùng ca/ngày có thể khó tối ưu.
* Có thể điều chỉnh tham số **số lần lặp** và **số lần restart** để có kết quả tốt hơn.
