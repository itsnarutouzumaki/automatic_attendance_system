import tkinter as tk
from tkinter import ttk
from attendance_taker import attendance_taker
from get_faces_from_camera_tkinter import registerStudent
from mailing_xls_attendance_file import send_email_with_attachment
from xls_attendance.xls_file_creator import xls_file_creator

root = tk.Tk()
root.title("Attendance System")
root.attributes("-fullscreen", True)
root.configure(bg="#1e1e1e")

registration_number = ""
course_id = ""
send_name = ""
send_course = ""
send_email = ""
course_students = []
student_entries = []

def switch_frame(target):
    for frame in [main_menu, register_frame, attendance_frame, send_frame, create_course_frame]:
        frame.pack_forget()
    target.pack(expand=True, fill="both")


def reset_all_entries():
    reg_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)
    send_name_entry.delete(0, tk.END)
    send_course_entry.delete(0, tk.END)
    send_email_entry.delete(0, tk.END)
    course_id_entry.delete(0, tk.END)
    for entry in student_entries:
        entry.destroy()
    student_entries.clear()
    create_new_student_entry()

def on_register_click():
    global registration_number
    name = reg_entry.get().strip()
    if name:
        register_error.config(text="")
        registration_number = name.lower()
        registerStudent(registration_number)
        print("Registration Number:", registration_number)
        reset_all_entries()
    else:
        register_error.config(text="Please enter registration number.")

def on_attendance_click():
    global course_id
    cid = course_entry.get().strip()
    if cid:
        attendance_error.config(text="")
        course_id = cid.strip().lower()
        attendance_taker(course_id)
        print("Course ID:", course_id)
        reset_all_entries()
    else:
        attendance_error.config(text="Please enter Course ID.")

def on_send_click():
    global send_name, send_course, send_email
    name = send_name_entry.get().strip()
    course = send_course_entry.get().strip()
    email = send_email_entry.get().strip()
    if name and course and email:
        send_error.config(text="")
        send_email_with_attachment(name, course, email)
        send_name, send_course, send_email = name, course, email
        print("Name:", send_name, "| Course:", send_course, "| Email:", send_email)
        reset_all_entries()
    else:
        send_error.config(text="All fields are required.")

def on_create_course():
    global course_students
    cid = course_id_entry.get().strip().lower()
    students = [e.get().strip().lower() for e in student_entries if e.get().strip().lower()]
    if cid and students:
        create_error.config(text="")
        print("Created Course ID:", cid)
        print("Registered Students:", students)
        course_students = students
        sorted_students = sorted(course_students, key=lambda x: x.lower())
        xls_file_creator(cid, sorted_students)
        reset_all_entries()
    else:
        create_error.config(text="Course ID and at least one student required.")

def on_enter_pressed(event):
    if event.widget.get().strip():
        create_new_student_entry()
        root.after(100, lambda: scroll_to_widget(student_entries[-1]))

def create_new_student_entry():
    entry = tk.Entry(student_inner_frame, font=("Arial", 14), width=40, justify="center")
    entry.pack(pady=5)
    entry.bind("<Return>", on_enter_pressed)
    student_entries.append(entry)
    entry.focus_set()

def scroll_to_widget(widget):
    canvas.update_idletasks()
    canvas.yview_moveto(widget.winfo_y() / max(1, student_inner_frame.winfo_height()))

# ----------------- Main Menu ----------------- #
main_menu = tk.Frame(root, bg="#1e1e1e")
btn_style = {"font": ("Arial", 18, "bold"), "width": 25, "height": 2, "padx": 10, "pady": 10}

main_menu_inner = tk.Frame(main_menu, bg="#1e1e1e")
main_menu_inner.place(relx=0.5, rely=0.5, anchor="center")

tk.Button(main_menu_inner, text="Register Student", bg="skyblue", command=lambda: switch_frame(register_frame), **btn_style).pack(pady=20)
tk.Button(main_menu_inner, text="Take Attendance", bg="lightgreen", command=lambda: switch_frame(attendance_frame), **btn_style).pack(pady=20)
tk.Button(main_menu_inner, text="Send XLSX File", bg="orange", command=lambda: switch_frame(send_frame), **btn_style).pack(pady=20)
tk.Button(main_menu_inner, text="Create Course", bg="plum", command=lambda: switch_frame(create_course_frame), **btn_style).pack(pady=20)
tk.Button(main_menu_inner, text="Exit", bg="red", fg="white", command=root.quit, **btn_style).pack(pady=20)  # <-- Exit Button

main_menu.pack(expand=True, fill="both")


# ---------------- Register Frame ---------------- #
register_frame = tk.Frame(root, bg="#1e1e1e")
inner_reg = tk.Frame(register_frame, bg="#1e1e1e")
inner_reg.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(inner_reg, text="Enter Registration Number", font=("Arial", 18), bg="#1e1e1e", fg="white").pack(pady=10)
reg_entry = tk.Entry(inner_reg, font=("Arial", 16), width=30, justify="center")
reg_entry.pack(pady=5)
tk.Button(inner_reg, text="Register", bg="green", fg="white", font=("Arial", 16), width=15, command=on_register_click).pack(pady=10)
register_error = tk.Label(inner_reg, text="", fg="red", bg="#1e1e1e", font=("Arial", 12))
register_error.pack()
tk.Button(inner_reg, text="Back", command=lambda: [reset_all_entries(), switch_frame(main_menu)], font=("Arial", 14), bg="gray", fg="white").pack(pady=10)

# ---------------- Attendance Frame ---------------- #
attendance_frame = tk.Frame(root, bg="#1e1e1e")
inner_attend = tk.Frame(attendance_frame, bg="#1e1e1e")
inner_attend.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(inner_attend, text="Enter Course ID", font=("Arial", 18), bg="#1e1e1e", fg="white").pack(pady=10)
course_entry = tk.Entry(inner_attend, font=("Arial", 16), width=30, justify="center")
course_entry.pack(pady=5)
tk.Button(inner_attend, text="Take Attendance", bg="green", fg="white", font=("Arial", 16), width=20, command=on_attendance_click).pack(pady=10)
attendance_error = tk.Label(inner_attend, text="", fg="red", bg="#1e1e1e", font=("Arial", 12))
attendance_error.pack()
tk.Button(inner_attend, text="Back", command=lambda: [reset_all_entries(), switch_frame(main_menu)], font=("Arial", 14), bg="gray", fg="white").pack(pady=10)

# ---------------- Send XLSX Frame ---------------- #
send_frame = tk.Frame(root, bg="#1e1e1e")
inner_send = tk.Frame(send_frame, bg="#1e1e1e")
inner_send.place(relx=0.5, rely=0.5, anchor="center")

for label, var in [("Enter Name", "name"), ("Enter Course ID", "course"), ("Enter Email", "email")]:
    tk.Label(inner_send, text=label, font=("Arial", 18), bg="#1e1e1e", fg="white").pack(pady=5)
    entry = tk.Entry(inner_send, font=("Arial", 16), width=30, justify="center")
    entry.pack(pady=5)
    if var == "name": send_name_entry = entry
    elif var == "course": send_course_entry = entry
    elif var == "email": send_email_entry = entry

tk.Button(inner_send, text="Send File", bg="green", fg="white", font=("Arial", 16), width=20, command=on_send_click).pack(pady=10)
send_error = tk.Label(inner_send, text="", fg="red", bg="#1e1e1e", font=("Arial", 12))
send_error.pack()
tk.Button(inner_send, text="Back", command=lambda: [reset_all_entries(), switch_frame(main_menu)], font=("Arial", 14), bg="gray", fg="white").pack(pady=10)

# ---------------- Create Course Frame ---------------- #
create_course_frame = tk.Frame(root, bg="#1e1e1e")
inner_create = tk.Frame(create_course_frame, bg="#1e1e1e")
inner_create.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(inner_create, text="Enter Course ID", font=("Arial", 18), bg="#1e1e1e", fg="white").pack(pady=5)
course_id_entry = tk.Entry(inner_create, font=("Arial", 16), width=30, justify="center")
course_id_entry.pack(pady=5)

tk.Label(inner_create, text="Add Registration Numbers (Press Enter to add more)", font=("Arial", 12), fg="lightgray", bg="#1e1e1e").pack(pady=5)

container = tk.Frame(inner_create)
container.pack(pady=10, expand=True, fill="both")

canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

student_inner_frame = tk.Frame(canvas, bg="#1e1e1e")
canvas.create_window((0, 0), window=student_inner_frame, anchor="n")

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

student_inner_frame.bind("<Configure>", on_configure)

def _on_mouse_wheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, 'units'))
canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, 'units'))

tk.Button(inner_create, text="Create Course", bg="green", fg="white", font=("Arial", 16), width=20, command=on_create_course).pack(pady=10)
create_error = tk.Label(inner_create, text="", fg="red", bg="#1e1e1e", font=("Arial", 12))
create_error.pack()
tk.Button(inner_create, text="Back", command=lambda: [reset_all_entries(), switch_frame(main_menu)], font=("Arial", 14), bg="gray", fg="white").pack(pady=10)

create_new_student_entry()

root.mainloop()
