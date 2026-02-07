import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os
from datetime import datetime, timedelta

LICENSE_FILE = "licenses.json"

def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return {}
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def refresh_tree():
    for item in tree.get_children():
        tree.delete(item)
    data = load_licenses()
    now = datetime.now()
    for key, val in data.items():
        dur = val['duration_days']
        start = val['start_date']
        status = "사용중" if val["in_use"] else "미사용"
        dur_display = "무기한"
        expired = False

        if dur:
            expiry = datetime.strptime(start, "%Y-%m-%d") + timedelta(days=dur)
            dur_display = f"{dur}일 (종료: {expiry.date()})"
            if now > expiry:
                status = "기간만료"
                expired = True

        tree.insert("", "end", iid=key, values=(key, start, dur_display, status))

    root.after(10000, refresh_tree)  # 10초마다 자동 새로고침

def add_license():
    show_editor()

def edit_license():
    selected = tree.selection()
    if not selected:
        return
    key = selected[0]
    show_editor(key)

def delete_license():
    selected = tree.selection()
    if not selected:
        return
    key = selected[0]
    if messagebox.askyesno("삭제 확인", f"{key} 삭제할까요?"):
        data = load_licenses()
        if key in data:
            data[key]['revoked'] = True  # 클라이언트 종료 유도
            save_licenses(data)
        del data[key]
        save_licenses(data)
        refresh_tree()

def show_editor(key=None):
    is_edit = key is not None
    data = load_licenses()
    lic = data.get(key, {
        "start_date": str(datetime.today().date()),
        "duration_days": None
    })

    top = tk.Toplevel(root)
    top.title("라이선스 수정" if is_edit else "라이선스 추가")
    top.geometry("350x200")
    top.lift()
    top.grab_set()

    tk.Label(top, text="라이선스 키").pack()
    entry_key = tk.Entry(top)
    entry_key.insert(0, key if key else "")
    entry_key.config(state="disabled" if is_edit else "normal")
    entry_key.pack()

    tk.Label(top, text="시작일 (YYYY-MM-DD)").pack()
    entry_start = tk.Entry(top)
    entry_start.insert(0, lic["start_date"])
    entry_start.pack()

    tk.Label(top, text="유효일수 (무기한이면 빈칸)").pack()
    entry_dur = tk.Entry(top)
    entry_dur.insert(0, str(lic["duration_days"]) if lic["duration_days"] else "")
    entry_dur.pack()

    def on_save():
        k = entry_key.get().strip()
        s = entry_start.get().strip()
        d = entry_dur.get().strip()

        try:
            datetime.strptime(s, "%Y-%m-%d")
        except:
            messagebox.showerror("오류", "날짜 형식이 잘못되었습니다.")
            return

        lic_data = load_licenses()

        if is_edit:
            if k in lic_data:
                lic_data[k]["start_date"] = s
                lic_data[k]["duration_days"] = int(d) if d else None
                lic_data[k]["revoked"] = True  # 현재 사용자 강제 종료
        else:
            lic_data[k] = {
                "in_use": False,
                "last_check": 0,
                "start_date": s,
                "duration_days": int(d) if d else None
            }

        save_licenses(lic_data)
        refresh_tree()
        top.destroy()

    tk.Button(top, text="저장", command=on_save).pack(pady=5)

# GUI 시작
root = tk.Tk()
root.title("라이선스 관리자")
root.geometry("700x400")

cols = ("키", "시작일", "기간", "상태")
tree = ttk.Treeview(root, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(pady=10, fill="both", expand=True)

btn_frame = tk.Frame(root)
btn_frame.pack()
tk.Button(btn_frame, text="➕ 추가", command=add_license).pack(side="left", padx=5)
tk.Button(btn_frame, text="✏️ 수정", command=edit_license).pack(side="left", padx=5)
tk.Button(btn_frame, text="🗑 삭제", command=delete_license).pack(side="left", padx=5)
tk.Button(btn_frame, text="🔁 새로고침", command=refresh_tree).pack(side="left", padx=5)

refresh_tree()
root.mainloop()
