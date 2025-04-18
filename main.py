import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog, messagebox
from attendance_taker import attendance_taker
from get_faces_from_camera_tkinter import registerStudent
from mailing_xls_attendance_file import send_email_with_attachment
from xls_attendance.xls_file_creator import xls_file_creator

# Load environment variables
load_dotenv()
PASSWORD = os.getenv("APP_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

def start_attendance_system(root_login):
    root_login.destroy()
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
        nonlocal registration_number
        name = reg_entry.get().strip()
        if name:
            register_error.config(text="")
            registration_number = name.lower()
            registerStudent(registration_number)
            reset_all_entries()
        else:
            register_error.config(text="Please enter registration number.")

    def on_attendance_click():
        nonlocal course_id
        cid = course_entry.get().strip()
        if cid:
            attendance_error.config(text="")
            course_id = cid.strip().lower()
            attendance_taker(course_id)
            reset_all_entries()
        else:
            attendance_error.config(text="Please enter Course ID.")

    def on_send_click():
        nonlocal send_name, send_course, send_email
        name = send_name_entry.get().strip()
        course = send_course_entry.get().strip()
        email = send_email_entry.get().strip()
        if name and course and email:
            send_error.config(text="")
            send_email_with_attachment(name, course, email)
            send_name, send_course, send_email = name, course, email
            reset_all_entries()
        else:
            send_error.config(text="All fields are required.")

    def on_create_course():
        nonlocal course_students
        cid = course_id_entry.get().strip().lower()
        students = [e.get().strip().lower() for e in student_entries if e.get().strip().lower()]
        if cid and students:
            create_error.config(text="")
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

    main_menu = tk.Frame(root, bg="#1e1e1e")
    btn_style = {"font": ("Arial", 18, "bold"), "width": 25, "height": 2, "padx": 10, "pady": 10}

    main_menu_inner = tk.Frame(main_menu, bg="#1e1e1e")
    main_menu_inner.place(relx=0.5, rely=0.5, anchor="center")

    tk.Button(main_menu_inner, text="Register Student", bg="skyblue", command=lambda: switch_frame(register_frame), **btn_style).pack(pady=20)
    tk.Button(main_menu_inner, text="Take Attendance", bg="lightgreen", command=lambda: switch_frame(attendance_frame), **btn_style).pack(pady=20)
    tk.Button(main_menu_inner, text="Send XLSX File", bg="orange", command=lambda: switch_frame(send_frame), **btn_style).pack(pady=20)
    tk.Button(main_menu_inner, text="Create Course", bg="plum", command=lambda: switch_frame(create_course_frame), **btn_style).pack(pady=20)
    tk.Button(main_menu_inner, text="Exit", bg="red", fg="white", command=root.destroy, **btn_style).pack(pady=20)

    main_menu.pack(expand=True, fill="both")

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
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
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

    tk.Button(inner_create, text="Create Course", bg="green", fg="white", font=("Arial", 16), width=20, command=on_create_course).pack(pady=10)
    create_error = tk.Label(inner_create, text="", fg="red", bg="#1e1e1e", font=("Arial", 12))
    create_error.pack()
    tk.Button(inner_create, text="Back", command=lambda: [reset_all_entries(), switch_frame(main_menu)], font=("Arial", 14), bg="gray", fg="white").pack(pady=10)

    create_new_student_entry()

    root.mainloop()

root_login = tk.Tk()
root_login.title("Login - Attendance System")
root_login.attributes("-fullscreen", True)
root_login.configure(bg="#1e1e1e")

def check_password():
    entered_password = password_entry.get()
    if entered_password == PASSWORD:
        start_attendance_system(root_login)
    elif entered_password == "":
        error_label.config(text="Please enter a password.")
    else:
        error_label.config(text="Incorrect Password. Try again.")

def toggle_password():
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
        toggle_button.config(text="Hide Password")
    else:
        password_entry.config(show='*')
        toggle_button.config(text="Show Password")

def show_reset_password():
    login_frame.pack_forget()
    reset_frame.pack(expand=True, fill="both")

def show_login():
    reset_frame.pack_forget()
    login_frame.pack(expand=True, fill="both")

def reset_password():
    secret = secret_entry.get()
    new_pass = new_pass_entry.get()
    confirm_pass = confirm_pass_entry.get()
    
    if not secret:
        reset_error_label.config(text="Please enter secret key.")
        return
    if not new_pass or not confirm_pass:
        reset_error_label.config(text="Please enter and confirm new password.")
        return
    
    if secret == SECRET_KEY:
        if new_pass == confirm_pass:
            # Read all existing environment variables
            env_lines = []
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
            
            # Update only the APP_PASSWORD
            updated_lines = []
            app_password_updated = False
            for line in env_lines:
                if line.strip().startswith('APP_PASSWORD='):
                    updated_lines.append(f"APP_PASSWORD={new_pass}\n")
                    app_password_updated = True
                else:
                    updated_lines.append(line)
            
            # If APP_PASSWORD wasn't found, add it
            if not app_password_updated:
                updated_lines.append(f"APP_PASSWORD={new_pass}\n")
            
            # Write back all variables
            with open('.env', 'w') as f:
                f.writelines(updated_lines)
            
            # Reload the environment variables
            load_dotenv(override=True)
            global PASSWORD
            PASSWORD = os.getenv("APP_PASSWORD")
            
            
            show_login()
        else:
            reset_error_label.config(text="Passwords do not match.")
    else:
        reset_error_label.config(text="Invalid Secret Key.")


# Login Frame
login_frame = tk.Frame(root_login, bg="#1e1e1e")
login_inner = tk.Frame(login_frame, bg="#1e1e1e")
login_inner.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(login_inner, text="Automatic Face-Based Attendance System", font=("Arial", 24, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
password_entry = tk.Entry(login_inner, font=("Arial", 16), width=30, justify="center", show="*")
password_entry.pack(pady=10)

toggle_button = tk.Button(login_inner, text="Show Password", bg="gray", fg="white", font=("Arial", 12), command=toggle_password)
toggle_button.pack(pady=5)

tk.Button(login_inner, text="Enter", bg="green", fg="white", font=("Arial", 16), width=15, command=check_password).pack(pady=10)
error_label = tk.Label(login_inner, text="", fg="red", bg="#1e1e1e", font=("Arial", 12))
error_label.pack(pady=5)

tk.Button(login_inner, text="Reset Password", bg="blue", fg="white", font=("Arial", 12), command=show_reset_password).pack(pady=5)

def on_enter(event):
    check_password()

password_entry.bind("<Return>", on_enter)

# Reset Password Frame
reset_frame = tk.Frame(root_login, bg="#1e1e1e")
reset_inner = tk.Frame(reset_frame, bg="#1e1e1e")
reset_inner.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(reset_inner, text="Reset Password", font=("Arial", 24, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)

tk.Label(reset_inner, text="Enter Secret Key:", font=("Arial", 16), fg="white", bg="#1e1e1e").pack(pady=5)
secret_entry = tk.Entry(reset_inner, font=("Arial", 16), width=30, justify="center", show="*")
secret_entry.pack(pady=5)

tk.Label(reset_inner, text="Enter New Password:", font=("Arial", 16), fg="white", bg="#1e1e1e").pack(pady=5)
new_pass_entry = tk.Entry(reset_inner, font=("Arial", 16), width=30, justify="center", show="*")
new_pass_entry.pack(pady=5)

tk.Label(reset_inner, text="Confirm New Password:", font=("Arial", 16), fg="white", bg="#1e1e1e").pack(pady=5)
confirm_pass_entry = tk.Entry(reset_inner, font=("Arial", 16), width=30, justify="center", show="*")
confirm_pass_entry.pack(pady=5)

tk.Button(reset_inner, text="Reset Password", bg="green", fg="white", font=("Arial", 16), width=15, command=reset_password).pack(pady=10)
reset_error_label = tk.Label(reset_inner, text="", fg="red", bg="#1e1e1e", font=("Arial", 12))
reset_error_label.pack(pady=5)

tk.Button(reset_inner, text="Back to Login", bg="blue", fg="white", font=("Arial", 12), command=show_login).pack(pady=5)

# Start with login frame
login_frame.pack(expand=True, fill="both")

root_login.mainloop()