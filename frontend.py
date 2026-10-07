
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import csv
import os
import subprocess
import sys
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_DIR = os.path.join(BASE_DIR, "Images")
DATA_DIR = os.path.join(BASE_DIR, "data")

STUDENTS_FILE = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# COLORS
# ============================================================

BG = "#0B1120"
SIDEBAR = "#111827"
CARD = "#172033"
CARD2 = "#1E293B"
BORDER = "#263449"

TEXT = "#F8FAFC"
MUTED = "#94A3B8"

BLUE = "#3B82F6"
CYAN = "#06B6D4"
GREEN = "#22C55E"
PURPLE = "#8B5CF6"
ORANGE = "#F59E0B"
RED = "#EF4444"

HOVER = "#263B5C"


# ============================================================
# ROOT
# ============================================================

root = tk.Tk()
root.title("AI Smart Attendance System")
root.geometry("1250x760")
root.minsize(1050, 650)
root.configure(bg=BG)


# ============================================================
# FONTS
# ============================================================

FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_HEADER = ("Segoe UI", 18, "bold")
FONT_SUB = ("Segoe UI", 10)
FONT_CARD = ("Segoe UI", 22, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_BUTTON = ("Segoe UI", 11, "bold")


# ============================================================
# ANIMATION HELPERS
# ============================================================

_animation_jobs = []

def pulse_widget(widget, on_color=GREEN, off_color="#14532D", interval=650):
    """Soft pulsing effect for status indicators. Uses Tkinter after()."""
    state = [False]
    def tick():
        if not widget.winfo_exists():
            return
        state[0] = not state[0]
        try:
            widget.configure(fg=on_color if state[0] else off_color)
            widget.after(interval, tick)
        except tk.TclError:
            pass
    widget.after(interval, tick)


def hover_glow(widget, normal_bg, hover_bg, normal_fg=TEXT, hover_fg=TEXT):
    def enter(_event):
        try:
            widget.configure(bg=hover_bg, fg=hover_fg)
        except tk.TclError:
            pass
    def leave(_event):
        try:
            widget.configure(bg=normal_bg, fg=normal_fg)
        except tk.TclError:
            pass
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


def animate_value(label, target, duration=700, prefix="", suffix=""):
    """Animate a numeric dashboard value without extra packages."""
    try:
        target = int(target)
    except (TypeError, ValueError):
        label.configure(text=f"{prefix}{target}{suffix}")
        return
    steps = max(1, min(35, duration // 25))
    current = [0]
    def step():
        current[0] += max(1, int(round(target / steps)))
        if current[0] >= target:
            current[0] = target
        try:
            label.configure(text=f"{prefix}{current[0]}{suffix}")
            if current[0] < target:
                label.after(max(15, duration // steps), step)
        except tk.TclError:
            pass
    label.configure(text=f"{prefix}0{suffix}")
    label.after(80, step)


def animated_progress_bar(parent, percentage):
    outer = tk.Frame(parent, bg=CARD2, height=8)
    outer.pack(fill="x", padx=28, pady=(18, 0))
    outer.pack_propagate(False)
    fill = tk.Frame(outer, bg=CYAN, height=8)
    fill.place(x=0, y=0, relheight=1, relwidth=0)
    target = max(0.0, min(1.0, percentage / 100.0))
    state = [0.0]
    def grow():
        state[0] = min(target, state[0] + 0.035)
        try:
            fill.place_configure(relwidth=state[0])
            if state[0] < target:
                fill.after(25, grow)
        except tk.TclError:
            pass
    fill.after(120, grow)
    return outer


def animate_canvas_line(canvas, width, color=CYAN):
    """Subtle moving accent used only as a professional visual detail."""
    try:
        canvas.delete("accent")
        x = [0]
        line = canvas.create_line(0, 1, 0, 1, fill=color, width=2, tags="accent")
        def move():
            if not canvas.winfo_exists():
                return
            x[0] += max(2, width // 90)
            if x[0] > width:
                x[0] = 0
            canvas.coords(line, max(0, x[0]-90), 1, x[0], 1)
            canvas.after(35, move)
        move()
    except tk.TclError:
        pass


def gentle_breathe(widget, base_bg, accent_bg, interval=1800):
    """Very slow visual breathing; deliberately restrained for a professional UI."""
    state = [False]
    def tick():
        if not widget.winfo_exists():
            return
        state[0] = not state[0]
        try:
            widget.configure(bg=accent_bg if state[0] else base_bg)
            widget.after(interval, tick)
        except tk.TclError:
            pass
    widget.after(interval, tick)


# ============================================================
# CSV HELPERS
# ============================================================

def ensure_csv_files():

    if not os.path.exists(STUDENTS_FILE):
        with open(
            STUDENTS_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)
            writer.writerow([
                "StudentID",
                "Name",
                "Image"
            ])


    if not os.path.exists(ATTENDANCE_FILE):
        with open(
            ATTENDANCE_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)
            writer.writerow([
                "StudentID",
                "Name",
                "Date",
                "Time"
            ])


ensure_csv_files()


def read_students():

    students = []

    try:

        with open(
            STUDENTS_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                if row.get("StudentID"):
                    students.append(row)

    except Exception as e:
        print("Student read error:", e)

    return students


def read_attendance():

    records = []

    try:

        with open(
            ATTENDANCE_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                if row.get("StudentID"):
                    records.append(row)

    except Exception as e:
        print("Attendance read error:", e)

    return records


# ============================================================
# MAIN CONTENT
# ============================================================

content = tk.Frame(
    root,
    bg=BG
)

content.pack(
    side="right",
    fill="both",
    expand=True
)


# ============================================================
# SIDEBAR
# ============================================================

sidebar = tk.Frame(
    root,
    bg=SIDEBAR,
    width=235
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


# ============================================================
# BRAND
# ============================================================

brand = tk.Frame(
    sidebar,
    bg=SIDEBAR
)

brand.pack(
    fill="x",
    padx=22,
    pady=(25, 30)
)


logo = tk.Label(
    brand,
    text="AI",
    font=("Segoe UI", 18, "bold"),
    fg="white",
    bg=BLUE,
    width=3
)

logo.pack(side="left")


brand_text = tk.Frame(
    brand,
    bg=SIDEBAR
)

brand_text.pack(
    side="left",
    padx=10
)


tk.Label(
    brand_text,
    text="SMART",
    font=("Segoe UI", 13, "bold"),
    fg=TEXT,
    bg=SIDEBAR
).pack(anchor="w")


tk.Label(
    brand_text,
    text="ATTENDANCE",
    font=("Segoe UI", 8, "bold"),
    fg=CYAN,
    bg=SIDEBAR
).pack(anchor="w")


# ============================================================
# NAVIGATION
# ============================================================

tk.Label(
    sidebar,
    text="MAIN MENU",
    font=("Segoe UI", 8, "bold"),
    fg=MUTED,
    bg=SIDEBAR
).pack(
    anchor="w",
    padx=25,
    pady=(0, 10)
)


def nav_button(text, command, icon):

    frame = tk.Frame(
        sidebar,
        bg=SIDEBAR
    )

    frame.pack(
        fill="x",
        padx=12,
        pady=3
    )


    button = tk.Button(
        frame,
        text=f"  {icon}   {text}",
        command=command,
        anchor="w",
        bd=0,
        relief="flat",
        font=FONT_NORMAL,
        fg=MUTED,
        bg=SIDEBAR,
        activeforeground=TEXT,
        activebackground=HOVER,
        cursor="hand2",
        padx=10,
        pady=10
    )

    button.pack(fill="x")


    def enter(event):
        button.configure(
            bg=HOVER,
            fg=TEXT
        )


    def leave(event):
        button.configure(
            bg=SIDEBAR,
            fg=MUTED
        )


    button.bind(
        "<Enter>",
        enter
    )

    button.bind(
        "<Leave>",
        leave
    )

    # Slight animated-feeling hover feedback without any external package.
    button.bind("<ButtonPress-1>", lambda _e: button.configure(bg=BLUE, fg="white"))
    button.bind("<ButtonRelease-1>", lambda _e: button.configure(bg=HOVER, fg=TEXT))

    return button


# ============================================================
# PAGE FUNCTIONS
# ============================================================

def clear_content():

    for widget in content.winfo_children():
        widget.destroy()


def show_page(page):

    clear_content()

    if page == "dashboard":
        build_dashboard()

    elif page == "attendance":
        build_attendance()

    elif page == "add":
        build_add_face()

    elif page == "students":
        build_students()

    elif page == "records":
        build_records()


nav_button(
    "Dashboard",
    lambda: show_page("dashboard"),
    "⌂"
)

nav_button(
    "Take Attendance",
    lambda: show_page("attendance"),
    "◉"
)

nav_button(
    "Add New Face",
    lambda: show_page("add"),
    "+"
)

nav_button(
    "Students",
    lambda: show_page("students"),
    "♙"
)

nav_button(
    "Attendance Records",
    lambda: show_page("records"),
    "▤"
)


# ============================================================
# SIDEBAR STATUS
# ============================================================

tk.Frame(
    sidebar,
    bg=SIDEBAR
).pack(
    fill="both",
    expand=True
)


status_box = tk.Frame(
    sidebar,
    bg="#172033",
    highlightbackground=BORDER,
    highlightthickness=1
)

status_box.pack(
    fill="x",
    padx=15,
    pady=(10, 15)
)


tk.Label(
    status_box,
    text="●  SYSTEM ONLINE",
    font=("Segoe UI", 9, "bold"),
    fg=GREEN,
    bg="#172033"
).pack(
    anchor="w",
    padx=15,
    pady=(13, 2)
)


tk.Label(
    status_box,
    text="AI Recognition Ready",
    font=("Segoe UI", 8),
    fg=MUTED,
    bg="#172033"
).pack(
    anchor="w",
    padx=15,
    pady=(0, 13)
)


pulse_widget(status_box.winfo_children()[0])
gentle_breathe(logo, BLUE, "#2563EB", 2100)


# ============================================================
# PAGE HEADER
# ============================================================

def page_header(title, subtitle):

    header = tk.Frame(
        content,
        bg=BG
    )

    header.pack(
        fill="x",
        padx=35,
        pady=(28, 10)
    )


    tk.Label(
        header,
        text=title,
        font=FONT_TITLE,
        fg=TEXT,
        bg=BG
    ).pack(anchor="w")


    tk.Label(
        header,
        text=subtitle,
        font=FONT_SUB,
        fg=MUTED,
        bg=BG
    ).pack(
        anchor="w",
        pady=(4, 0)
    )

    accent = tk.Canvas(header, height=3, bg=BG, bd=0, highlightthickness=0)
    accent.pack(fill="x", pady=(12, 0))
    accent.bind("<Configure>", lambda e: animate_canvas_line(accent, e.width))


# ============================================================
# STAT CARD
# ============================================================

def stat_card(parent, title, value, icon, color):

    card = tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=7
    )

    top = tk.Frame(card, bg=CARD)
    top.pack(fill="x", padx=18, pady=(15, 3))

    icon_label = tk.Label(
        top, text=icon, font=("Segoe UI", 17, "bold"),
        fg=color, bg=CARD
    )
    icon_label.pack(side="right")

    tk.Label(
        card, text=title, font=FONT_SMALL, fg=MUTED, bg=CARD
    ).pack(anchor="w", padx=18)

    value_label = tk.Label(
        card, text="0" if isinstance(value, int) else str(value),
        font=FONT_CARD, fg=TEXT, bg=CARD
    )
    value_label.pack(anchor="w", padx=18, pady=(2, 15))

    hover_glow(card, CARD, HOVER)
    card.bind("<Enter>", lambda _e: card.configure(highlightbackground="#31537A"))
    card.bind("<Leave>", lambda _e: card.configure(highlightbackground=BORDER))
    for child in (top, icon_label, value_label):
        child.bind("<Enter>", lambda _e, c=card: c.configure(bg=HOVER))
        child.bind("<Leave>", lambda _e, c=card: c.configure(bg=CARD))

    if isinstance(value, int):
        animate_value(value_label, value)
    return card


# ============================================================
# DASHBOARD
# ============================================================

def build_dashboard():

    page_header(
        "Welcome to AI Smart Attendance",
        "Intelligent face recognition • Automated attendance • Real-time records"
    )

    students = read_students()
    attendance = read_attendance()
    today = datetime.now().strftime("%Y-%m-%d")
    today_records = [row for row in attendance if row.get("Date") == today]
    unique_today = set(row.get("StudentID") for row in today_records)

    total_students = len(students)
    present_count = len(unique_today)
    attendance_percentage = int((present_count / total_students) * 100) if total_students else 0

    # Futuristic live status strip
    status = tk.Frame(content, bg=CARD2, highlightbackground=BORDER, highlightthickness=1)
    status.pack(fill="x", padx=35, pady=(4, 8))
    status_dot = tk.Label(status, text="●", font=("Segoe UI", 14, "bold"), fg=GREEN, bg=CARD2)
    status_dot.pack(side="left", padx=(18, 5), pady=10)
    tk.Label(status, text="SYSTEM ONLINE", font=("Segoe UI", 9, "bold"), fg=GREEN, bg=CARD2).pack(side="left")
    tk.Label(status, text="  •  AI RECOGNITION READY", font=("Segoe UI", 9), fg=MUTED, bg=CARD2).pack(side="left")
    live_clock = tk.Label(status, text="", font=("Consolas", 9, "bold"), fg=CYAN, bg=CARD2)
    live_clock.pack(side="right", padx=18)
    pulse_widget(status_dot)

    def update_clock():
        if live_clock.winfo_exists():
            live_clock.configure(text=datetime.now().strftime("%d %b %Y   %H:%M:%S"))
            live_clock.after(1000, update_clock)
    update_clock()

    stats = tk.Frame(content, bg=BG)
    stats.pack(fill="x", padx=28, pady=10)
    stat_card(stats, "TOTAL STUDENTS", total_students, "♙", BLUE)
    stat_card(stats, "TODAY PRESENT", present_count, "✓", GREEN)
    stat_card(stats, "TOTAL RECORDS", len(attendance), "▤", PURPLE)
    stat_card(stats, "ATTENDANCE", attendance_percentage, "%", CYAN)

    action_area = tk.Frame(content, bg=BG)
    action_area.pack(fill="both", expand=True, padx=35, pady=12)

    # Attendance action card
    attendance_card = tk.Frame(action_area, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    attendance_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
    tk.Label(attendance_card, text="◉", font=("Segoe UI", 38, "bold"), fg=BLUE, bg=CARD).pack(anchor="w", padx=28, pady=(25, 3))
    tk.Label(attendance_card, text="Take Attendance", font=FONT_HEADER, fg=TEXT, bg=CARD).pack(anchor="w", padx=28)
    tk.Label(attendance_card, text="Use AI face recognition to automatically\nidentify students and record attendance.", font=FONT_NORMAL, fg=MUTED, bg=CARD, justify="left").pack(anchor="w", padx=28, pady=(8, 12))
    animated_progress_bar(attendance_card, attendance_percentage)
    tk.Label(attendance_card, text=f"Today's attendance: {attendance_percentage}%", font=FONT_SMALL, fg=CYAN, bg=CARD).pack(anchor="w", padx=28, pady=(7, 10))
    btn1 = tk.Button(attendance_card, text="  START ATTENDANCE  →", command=lambda: show_page("attendance"), font=FONT_BUTTON, fg="white", bg=BLUE, activebackground="#2563EB", activeforeground="white", bd=0, cursor="hand2", padx=18, pady=12)
    btn1.pack(anchor="w", padx=28)
    hover_glow(btn1, BLUE, "#2563EB", "white", "white")
    hover_glow(attendance_card, CARD, HOVER)

    # Registration action card
    add_card = tk.Frame(action_area, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    add_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
    tk.Label(add_card, text="+", font=("Segoe UI", 40, "bold"), fg=CYAN, bg=CARD).pack(anchor="w", padx=28, pady=(25, 3))
    tk.Label(add_card, text="Register New Student", font=FONT_HEADER, fg=TEXT, bg=CARD).pack(anchor="w", padx=28)
    tk.Label(add_card, text="Capture a student's face and save their\nprofile for future recognition.", font=FONT_NORMAL, fg=MUTED, bg=CARD, justify="left").pack(anchor="w", padx=28, pady=(8, 22))
    btn2 = tk.Button(add_card, text="  ADD NEW FACE  +", command=lambda: show_page("add"), font=FONT_BUTTON, fg="white", bg=CYAN, activebackground="#0891B2", activeforeground="white", bd=0, cursor="hand2", padx=18, pady=12)
    btn2.pack(anchor="w", padx=28)
    hover_glow(btn2, CYAN, "#0891B2", "white", "white")
    hover_glow(add_card, CARD, HOVER)


# ============================================================
# ATTENDANCE PAGE
# ============================================================

def build_attendance():

    page_header(
        "Take Attendance",
        "Launch the AI-powered face recognition attendance system"
    )


    center = tk.Frame(
        content,
        bg=BG
    )

    center.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=20
    )


    card = tk.Frame(
        center,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.pack(
        expand=True,
        fill="both"
    )


    tk.Label(
        card,
        text="📷",
        font=("Segoe UI", 55),
        fg=BLUE,
        bg=CARD
    ).pack(
        pady=(60, 10)
    )


    tk.Label(
        card,
        text="AI Face Recognition",
        font=("Segoe UI", 24, "bold"),
        fg=TEXT,
        bg=CARD
    ).pack()


    tk.Label(
        card,
        text="Position your face in front of the camera.\n"
             "The system will identify registered students\n"
             "and record attendance automatically.",
        font=FONT_NORMAL,
        fg=MUTED,
        bg=CARD,
        justify="center"
    ).pack(pady=15)


    tk.Button(
        card,
        text="  START CAMERA  ▶",
        command=start_attendance,
        font=("Segoe UI", 12, "bold"),
        fg="white",
        bg=BLUE,
        activebackground="#2563EB",
        activeforeground="white",
        bd=0,
        cursor="hand2",
        padx=30,
        pady=14
    ).pack(pady=15)


    tk.Label(
        card,
        text="Attendance is recorded only once per student per day.",
        font=FONT_SMALL,
        fg=GREEN,
        bg=CARD
    ).pack(pady=5)


def start_attendance():

    try:

        subprocess.Popen(
            [
                sys.executable,
                os.path.join(BASE_DIR, "main.py")
            ],
            cwd=BASE_DIR
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Could not start attendance system:\n\n{e}"
        )


# ============================================================
# ADD NEW FACE
# ============================================================

def build_add_face():

    page_header(
        "Register New Student",
        "Capture a clear face image for accurate AI recognition"
    )


    form = tk.Frame(
        content,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    form.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=20
    )


    tk.Label(
        form,
        text="Student Information",
        font=FONT_HEADER,
        fg=TEXT,
        bg=CARD
    ).pack(
        anchor="w",
        padx=35,
        pady=(30, 5)
    )


    tk.Label(
        form,
        text="Enter the student's details before capturing their face.",
        font=FONT_NORMAL,
        fg=MUTED,
        bg=CARD
    ).pack(
        anchor="w",
        padx=35,
        pady=(0, 25)
    )


    # ID

    tk.Label(
        form,
        text="Student ID",
        font=("Segoe UI", 10, "bold"),
        fg=TEXT,
        bg=CARD
    ).pack(
        anchor="w",
        padx=35
    )


    id_entry = tk.Entry(
        form,
        font=FONT_NORMAL,
        fg=TEXT,
        bg=CARD2,
        insertbackground=TEXT,
        relief="flat"
    )

    id_entry.pack(
        fill="x",
        padx=35,
        pady=(6, 18),
        ipady=9
    )


    # Name

    tk.Label(
        form,
        text="Student Name",
        font=("Segoe UI", 10, "bold"),
        fg=TEXT,
        bg=CARD
    ).pack(
        anchor="w",
        padx=35
    )


    name_entry = tk.Entry(
        form,
        font=FONT_NORMAL,
        fg=TEXT,
        bg=CARD2,
        insertbackground=TEXT,
        relief="flat"
    )

    name_entry.pack(
        fill="x",
        padx=35,
        pady=(6, 20),
        ipady=9
    )


    instruction = tk.Label(
        form,
        text="Tip: Face the camera directly and use good lighting.",
        font=FONT_SMALL,
        fg=ORANGE,
        bg=CARD
    )

    instruction.pack(
        pady=5
    )


    result_label = tk.Label(
        form,
        text="",
        font=FONT_NORMAL,
        fg=GREEN,
        bg=CARD
    )

    result_label.pack(
        pady=5
    )


    # --------------------------------------------------------
    # FACE DETECTOR
    # --------------------------------------------------------

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )


    def capture_face():

        student_id = id_entry.get().strip()
        name = name_entry.get().strip()


        if not student_id or not name:

            messagebox.showwarning(
                "Missing Information",
                "Please enter both Student ID and Student Name."
            )

            return


        # Check whether this Student ID already exists.
        # Existing students are UPDATED instead of creating duplicates.
        existing_student = None

        for student in read_students():
            if student.get("StudentID") == student_id:
                existing_student = student
                break

        camera = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )


        if not camera.isOpened():

            messagebox.showerror(
                "Camera Error",
                "Could not open the webcam."
            )

            return


        window_name = "Register Face"

        captured = False
        saved_path = None


        while True:

            ret, frame = camera.read()


            if not ret:
                break


            display = frame.copy()


            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )


            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )


            # ------------------------------------------------
            # DRAW DETECTED FACE
            # ------------------------------------------------

            if len(faces) > 0:

                # Choose largest face

                face = max(
                    faces,
                    key=lambda item: item[2] * item[3]
                )

                x, y, w, h = face


                cv2.rectangle(
                    display,
                    (x, y),
                    (x + w, y + h),
                    (59, 130, 246),
                    3
                )


                cv2.putText(
                    display,
                    "FACE DETECTED",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )


            else:

                cv2.putText(
                    display,
                    "NO FACE DETECTED",
                    (30, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )


            cv2.putText(
                display,
                "SPACE = Capture",
                (30, 480),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


            cv2.putText(
                display,
                "Q = Cancel",
                (30, 515),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (220, 220, 220),
                2
            )


            cv2.imshow(
                window_name,
                display
            )


            key = cv2.waitKey(1) & 0xFF


            # ------------------------------------------------
            # CAPTURE
            # ------------------------------------------------

            if key == ord(" "):

                if len(faces) == 0:

                    messagebox.showwarning(
                        "No Face Detected",
                        "Please position your face clearly in front of the camera."
                    )

                    continue


                face = max(
                    faces,
                    key=lambda item: item[2] * item[3]
                )

                x, y, w, h = face


                # Add padding around face

                padding = int(
                    min(w, h) * 0.25
                )


                x1 = max(
                    0,
                    x - padding
                )

                y1 = max(
                    0,
                    y - padding
                )

                x2 = min(
                    frame.shape[1],
                    x + w + padding
                )

                y2 = min(
                    frame.shape[0],
                    y + h + padding
                )


                face_crop = frame[
                    y1:y2,
                    x1:x2
                ]


                # Make sure crop is valid

                if face_crop.size == 0:

                    continue


                filename = (
                    f"{name}_{student_id}.jpg"
                )


                saved_path = os.path.join(
                    IMAGE_DIR,
                    filename
                )


                cv2.imwrite(
                    saved_path,
                    face_crop
                )


                captured = True

                break


            elif key == ord("q"):

                break


        camera.release()

        cv2.destroyAllWindows()


        # ----------------------------------------------------
        # SAVE / UPDATE STUDENT
        # ----------------------------------------------------

        if captured and saved_path:

            students = read_students()
            updated = False

            # If the ID already exists, update that student's
            # name and face image instead of creating a duplicate.
            for student in students:
                if student.get("StudentID") == student_id:
                    student["Name"] = name
                    student["Image"] = saved_path
                    updated = True
                    break

            # If it is a new ID, add a new student.
            if not updated:
                students.append({
                    "StudentID": student_id,
                    "Name": name,
                    "Image": saved_path
                })

            # Rewrite ONLY students.csv.
            # attendance.csv is never changed.
            with open(
                STUDENTS_FILE,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)
                writer.writerow(["StudentID", "Name", "Image"])

                for student in students:
                    writer.writerow([
                        student.get("StudentID", ""),
                        student.get("Name", ""),
                        student.get("Image", "")
                    ])

            if updated:
                result_label.config(
                    text=f"✓ {name}'s face was updated successfully!",
                    fg=GREEN
                )

                messagebox.showinfo(
                    "Face Updated",
                    f"{name}'s face image has been updated successfully.\n\n"
                    f"Student ID: {student_id}\n\n"
                    f"Old attendance records were kept safely."
                )
            else:
                result_label.config(
                    text=f"✓ {name} registered successfully!",
                    fg=GREEN
                )

                messagebox.showinfo(
                    "Registration Complete",
                    f"{name} has been registered successfully.\n\n"
                    f"Student ID: {student_id}\n\n"
                    f"Face image saved as:\n"
                    f"{os.path.basename(saved_path)}"
                )

            id_entry.delete(
                0,
                tk.END
            )

            name_entry.delete(
                0,
                tk.END
            )


    tk.Button(
        form,
        text="  CAPTURE FACE  📷",
        command=capture_face,
        font=FONT_BUTTON,
        fg="white",
        bg=CYAN,
        activebackground="#0891B2",
        activeforeground="white",
        bd=0,
        cursor="hand2",
        padx=25,
        pady=12
    ).pack(
        pady=15
    )


# ============================================================
# STUDENTS PAGE
# ============================================================

def build_students():

    page_header(
        "Registered Students",
        "Students currently enrolled in the AI recognition system"
    )


    students = read_students()


    container = tk.Frame(
        content,
        bg=BG
    )

    container.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=15
    )


    top = tk.Frame(
        container,
        bg=BG
    )

    top.pack(
        fill="x",
        pady=(0, 12)
    )


    tk.Label(
        top,
        text=f"{len(students)} registered student(s)",
        font=FONT_NORMAL,
        fg=MUTED,
        bg=BG
    ).pack(side="left")


    tk.Button(
        top,
        text="+ Add Student",
        command=lambda: show_page("add"),
        font=("Segoe UI", 9, "bold"),
        fg="white",
        bg=BLUE,
        activebackground="#2563EB",
        bd=0,
        cursor="hand2",
        padx=15,
        pady=8
    ).pack(side="right")


    table_frame = tk.Frame(
        container,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    table_frame.pack(
        fill="both",
        expand=True
    )


    columns = (
        "id",
        "name",
        "image",
        "status"
    )


    style = ttk.Style()

    try:
        style.theme_use("clam")
    except:
        pass


    style.configure(
        "Student.Treeview",
        background=CARD,
        foreground=TEXT,
        fieldbackground=CARD,
        rowheight=42,
        borderwidth=0,
        font=("Segoe UI", 10)
    )


    style.configure(
        "Student.Treeview.Heading",
        background=CARD2,
        foreground=CYAN,
        font=("Segoe UI", 9, "bold"),
        borderwidth=0
    )


    style.map(
        "Student.Treeview",
        background=[
            ("selected", HOVER)
        ],
        foreground=[
            ("selected", TEXT)
        ]
    )


    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Student.Treeview"
    )


    tree.heading(
        "id",
        text="STUDENT ID"
    )

    tree.heading(
        "name",
        text="NAME"
    )

    tree.heading(
        "image",
        text="FACE IMAGE"
    )

    tree.heading(
        "status",
        text="STATUS"
    )


    tree.column(
        "id",
        width=150
    )

    tree.column(
        "name",
        width=250
    )

    tree.column(
        "image",
        width=350
    )

    tree.column(
        "status",
        width=150
    )


    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )


    tree.configure(
        yscrollcommand=scrollbar.set
    )


    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )


    for student in students:

        image_name = os.path.basename(
            student.get("Image", "")
        )


        tree.insert(
            "",
            "end",
            values=(
                student.get("StudentID", ""),
                student.get("Name", ""),
                image_name,
                "● Active"
            )
        )


# ============================================================
# ATTENDANCE RECORDS
# ============================================================

def build_records():

    page_header(
        "Attendance Records",
        "Complete attendance history with date and exact time"
    )


    records = read_attendance()


    container = tk.Frame(
        content,
        bg=BG
    )

    container.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=15
    )


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    today_records = [
        r
        for r in records
        if r.get("Date") == today
    ]


    summary = tk.Frame(
        container,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    summary.pack(
        fill="x",
        pady=(0, 15)
    )


    left = tk.Frame(
        summary,
        bg=CARD
    )

    left.pack(
        side="left",
        padx=20,
        pady=12
    )


    tk.Label(
        left,
        text="TODAY'S ATTENDANCE",
        font=("Segoe UI", 9, "bold"),
        fg=MUTED,
        bg=CARD
    ).pack(anchor="w")


    tk.Label(
        left,
        text=str(len(today_records)),
        font=("Segoe UI", 24, "bold"),
        fg=GREEN,
        bg=CARD
    ).pack(anchor="w")


    tk.Label(
        summary,
        text=datetime.now().strftime(
            "%d %B %Y"
        ),
        font=FONT_NORMAL,
        fg=CYAN,
        bg=CARD
    ).pack(
        side="right",
        padx=25
    )


    table_frame = tk.Frame(
        container,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    table_frame.pack(
        fill="both",
        expand=True
    )


    columns = (
        "id",
        "name",
        "date",
        "time"
    )


    style = ttk.Style()

    style.configure(
        "Record.Treeview",
        background=CARD,
        foreground=TEXT,
        fieldbackground=CARD,
        rowheight=45,
        font=("Segoe UI", 10)
    )


    style.configure(
        "Record.Treeview.Heading",
        background=CARD2,
        foreground=CYAN,
        font=("Segoe UI", 9, "bold")
    )


    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Record.Treeview"
    )


    tree.heading(
        "id",
        text="STUDENT ID"
    )

    tree.heading(
        "name",
        text="STUDENT NAME"
    )

    tree.heading(
        "date",
        text="DATE"
    )

    tree.heading(
        "time",
        text="TIME"
    )


    tree.column(
        "id",
        width=180
    )

    tree.column(
        "name",
        width=300
    )

    tree.column(
        "date",
        width=220
    )

    tree.column(
        "time",
        width=200
    )


    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )


    tree.configure(
        yscrollcommand=scrollbar.set
    )


    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )


    for row in reversed(records):

        # Explicitly get date and time

        date_value = row.get(
            "Date",
            ""
        )

        time_value = row.get(
            "Time",
            ""
        )


        tree.insert(
            "",
            "end",
            values=(
                row.get(
                    "StudentID",
                    ""
                ),

                row.get(
                    "Name",
                    ""
                ),

                date_value,

                time_value
            )
        )


# ============================================================
# START
# ============================================================

show_page("dashboard")

root.mainloop()

