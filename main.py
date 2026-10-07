
import os
import csv
import time
from datetime import datetime

import cv2
from deepface import DeepFace


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_DIR = os.path.join(BASE_DIR, "Images")
DATA_DIR = os.path.join(BASE_DIR, "data")

STUDENTS_FILE = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")


# ============================================================
# DEEPFACE SETTINGS
# ============================================================

MODEL_NAME = "VGG-Face"
DETECTOR_BACKEND = "opencv"

# VGG-Face cosine distance normally works well around 0.40-0.50.
# We use the best distance among all registered students.
DISTANCE_THRESHOLD = 0.50

# Recognition every 2 seconds.
RECOGNITION_INTERVAL = 2.0

# Wait after successful attendance.
ATTENDANCE_COOLDOWN = 5


# ============================================================
# CAMERA SETTINGS
# ============================================================

CAMERA_INDEXES = [0, 1]


# ============================================================
# CSV HEADERS
# ============================================================

STUDENT_HEADERS = [
    "StudentID",
    "Name",
    "Image"
]

ATTENDANCE_HEADERS = [
    "StudentID",
    "Name",
    "Date",
    "Time"
]


# ============================================================
# SETUP FILES
# ============================================================

def setup_files():

    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(STUDENTS_FILE):

        with open(
            STUDENTS_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)
            writer.writerow(STUDENT_HEADERS)

    if not os.path.exists(ATTENDANCE_FILE):

        with open(
            ATTENDANCE_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)
            writer.writerow(ATTENDANCE_HEADERS)


# ============================================================
# LOAD STUDENTS
# ============================================================

def load_students():

    students = {}

    if not os.path.exists(STUDENTS_FILE):

        print("ERROR: students.csv not found.")
        return students

    try:

        with open(
            STUDENTS_FILE,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:

                print("ERROR: students.csv is empty.")
                return students

            print("\nStudents found in CSV:")
            print("-" * 60)

            for row in reader:

                student_id = str(
                    row.get("StudentID", "")
                ).strip()

                name = str(
                    row.get("Name", "")
                ).strip()

                image = str(
                    row.get("Image", "")
                ).strip()

                if not student_id:
                    continue

                if not name:
                    name = "Unknown"

                students[student_id] = {
                    "StudentID": student_id,
                    "Name": name,
                    "Image": image
                }

                print(
                    f"{student_id} | {name} | {image}"
                )

    except Exception as error:

        print(
            "ERROR reading students.csv:",
            error
        )

    print("-" * 60)
    print(
        f"Total students loaded: {len(students)}"
    )

    return students


# ============================================================
# GET STUDENT IMAGE PATH
# ============================================================

def get_student_image_path(image_name):

    if not image_name:
        return ""

    image_name = image_name.strip()

    # Absolute path
    if os.path.isabs(image_name):
        return image_name

    return os.path.join(
        IMAGE_DIR,
        image_name
    )


# ============================================================
# CHECK STUDENT IMAGES
# ============================================================

def check_student_images(students):

    print("\nChecking registered student images...")
    print("=" * 70)

    valid_students = {}

    for student_id, student in students.items():

        image_path = get_student_image_path(
            student["Image"]
        )

        print(
            f"\nStudent: {student['Name']}"
        )

        print(
            f"ID:      {student_id}"
        )

        print(
            f"Image:   {image_path}"
        )

        if not os.path.exists(image_path):

            print(
                "[MISSING] Image file does not exist."
            )

            continue

        # Actually try reading the image
        image = cv2.imread(image_path)

        if image is None:

            print(
                "[ERROR] Image exists but OpenCV cannot read it."
            )

            continue

        height, width = image.shape[:2]

        if height < 50 or width < 50:

            print(
                "[ERROR] Image is too small."
            )

            continue

        print(
            f"[OK] Image loaded: {width} x {height}"
        )

        valid_students[student_id] = student

    print("\n" + "=" * 70)

    print(
        f"Valid student images: "
        f"{len(valid_students)}/{len(students)}"
    )

    print("=" * 70)

    return valid_students


# ============================================================
# CHECK ATTENDANCE
# ============================================================

def attendance_already_marked(
    student_id,
    date
):

    if not os.path.exists(ATTENDANCE_FILE):
        return False

    try:

        with open(
            ATTENDANCE_FILE,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                existing_id = str(
                    row.get("StudentID", "")
                ).strip()

                existing_date = str(
                    row.get("Date", "")
                ).strip()

                if (
                    existing_id == str(student_id)
                    and existing_date == date
                ):

                    return True

    except Exception as error:

        print(
            "ERROR checking attendance:",
            error
        )

    return False


# ============================================================
# MARK ATTENDANCE
# ============================================================

def mark_attendance(
    student_id,
    name
):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    if attendance_already_marked(
        student_id,
        date
    ):

        print(
            f"[ALREADY MARKED] "
            f"{student_id} - {name}"
        )

        return False, "Already Marked"

    try:

        with open(
            ATTENDANCE_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                student_id,
                name,
                date,
                current_time
            ])

        print(
            f"[ATTENDANCE MARKED] "
            f"{student_id} - {name} "
            f"at {current_time}"
        )

        return True, "Attendance Marked"

    except Exception as error:

        print(
            "ERROR writing attendance:",
            error
        )

        return False, "Error"


# ============================================================
# RECOGNIZE STUDENT
# ============================================================

def recognize_student(
    frame,
    students
):

    if not students:
        return None, None, None

    temp_image = os.path.join(
        BASE_DIR,
        "_temp_camera_frame.jpg"
    )

    best_student_id = None
    best_name = None
    best_distance = 999

    try:

        # Save current camera frame
        success = cv2.imwrite(
            temp_image,
            frame
        )

        if not success:

            print(
                "ERROR: Could not save camera frame."
            )

            return None, None, None

        # ----------------------------------------------------
        # Compare against EVERY registered student
        # ----------------------------------------------------

        for student_id, student in students.items():

            image_path = get_student_image_path(
                student["Image"]
            )

            if not os.path.exists(image_path):
                continue

            try:

                result = DeepFace.verify(

                    img1_path=temp_image,

                    img2_path=image_path,

                    model_name=MODEL_NAME,

                    detector_backend=DETECTOR_BACKEND,

                    distance_metric="cosine",

                    enforce_detection=False,

                    align=True
                )

                distance = result.get(
                    "distance",
                    999
                )

                try:
                    distance = float(distance)
                except:
                    distance = 999

                print(
                    f"Checking "
                    f"{student['Name']} "
                    f"({student_id}) "
                    f"-> distance: "
                    f"{distance:.4f}"
                )

                # Keep the BEST match
                if distance < best_distance:

                    best_distance = distance

                    best_student_id = student_id

                    best_name = student["Name"]

            except Exception as error:

                print(
                    f"Recognition error for "
                    f"{student['Name']}: "
                    f"{error}"
                )

                continue

        # ----------------------------------------------------
        # Check best match against threshold
        # ----------------------------------------------------

        if (
            best_student_id is not None
            and best_distance <= DISTANCE_THRESHOLD
        ):

            print(
                "\nBEST MATCH:"
            )

            print(
                f"Student: {best_name}"
            )

            print(
                f"ID: {best_student_id}"
            )

            print(
                f"Distance: {best_distance:.4f}"
            )

            print(
                "Result: FACE RECOGNIZED"
            )

            return (
                best_student_id,
                best_name,
                best_distance
            )

        # No sufficiently close match

        if best_student_id is not None:

            print(
                f"\nBest match was "
                f"{best_name} "
                f"({best_student_id})"
            )

            print(
                f"Distance: {best_distance:.4f}"
            )

            print(
                f"Required: <= "
                f"{DISTANCE_THRESHOLD}"
            )

        print(
            "Result: FACE NOT RECOGNIZED"
        )

    except Exception as error:

        print(
            "\nERROR during face recognition:"
        )

        print(error)

    finally:

        try:

            if os.path.exists(temp_image):
                os.remove(temp_image)

        except:
            pass

    return None, None, None


# ============================================================
# DRAW STATUS
# ============================================================

def draw_status(
    frame,
    message,
    color,
    y
):

    cv2.putText(

        frame,

        message,

        (20, y),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.70,

        color,

        2,

        cv2.LINE_AA
    )


# ============================================================
# OPEN CAMERA
# ============================================================

def open_camera():

    print("\nTrying to open webcam...")

    # --------------------------------------------------------
    # Try DirectShow first
    # --------------------------------------------------------

    for camera_index in CAMERA_INDEXES:

        print(
            f"Trying camera index {camera_index} "
            f"with DirectShow..."
        )

        camera = cv2.VideoCapture(
            camera_index,
            cv2.CAP_DSHOW
        )

        if camera.isOpened():

            # Try to read an actual frame
            success, frame = camera.read()

            if success and frame is not None:

                print(
                    f"[OK] Camera {camera_index} opened."
                )

                return camera

            camera.release()

    # --------------------------------------------------------
    # Try normal OpenCV backend
    # --------------------------------------------------------

    for camera_index in CAMERA_INDEXES:

        print(
            f"Trying camera index {camera_index} "
            f"with default backend..."
        )

        camera = cv2.VideoCapture(
            camera_index
        )

        if camera.isOpened():

            success, frame = camera.read()

            if success and frame is not None:

                print(
                    f"[OK] Camera {camera_index} opened."
                )

                return camera

            camera.release()

    print("\nERROR: No webcam could be opened.")

    print(
        "\nPossible reasons:"
    )

    print(
        "1. Another application is using the camera."
    )

    print(
        "2. Windows camera permission is disabled."
    )

    print(
        "3. Camera index is different."
    )

    print(
        "4. Webcam driver problem."
    )

    return None


# ============================================================
# MAIN ATTENDANCE SYSTEM
# ============================================================

def run_attendance():

    print("\n")
    print("=" * 70)
    print("              AI SMART ATTENDANCE SYSTEM")
    print("=" * 70)

    # --------------------------------------------------------
    # Setup
    # --------------------------------------------------------

    setup_files()

    # --------------------------------------------------------
    # Load students
    # --------------------------------------------------------

    students = load_students()

    if not students:

        print(
            "\nERROR: No students registered."
        )

        print(
            "\nExpected students.csv:"
        )

        print(
            "StudentID,Name,Image"
        )

        print(
            "101,Bhoomika,101_Bhoomika.jpg"
        )

        print(
            "102,Alice,102_Alice.jpg"
        )

        input(
            "\nPress ENTER to close..."
        )

        return

    # --------------------------------------------------------
    # Check student images
    # --------------------------------------------------------

    students = check_student_images(
        students
    )

    if not students:

        print(
            "\nERROR: No valid student images found."
        )

        print(
            f"\nImages folder:"
        )

        print(
            IMAGE_DIR
        )

        input(
            "\nPress ENTER to close..."
        )

        return

    # --------------------------------------------------------
    # Open camera
    # --------------------------------------------------------

    camera = open_camera()

    if camera is None:

        input(
            "\nPress ENTER to close..."
        )

        return

    # --------------------------------------------------------
    # Camera resolution
    # --------------------------------------------------------

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    print("\n")
    print("=" * 70)
    print("WEBCAM STARTED")
    print("=" * 70)

    print(
        "Look directly at the camera."
    )

    print(
        "Press Q to stop attendance."
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------

    last_recognition_time = 0

    last_attendance_time = 0

    status_message = "Waiting for face..."

    status_color = (
        255,
        255,
        255
    )

    recognized_student = None

    # --------------------------------------------------------
    # Camera loop
    # --------------------------------------------------------

    while True:

        success, frame = camera.read()

        if not success:

            print(
                "\nERROR: Camera frame could not be read."
            )

            break

        # Mirror image
        frame = cv2.flip(
            frame,
            1
        )

        current_time = time.time()

        # ----------------------------------------------------
        # Recognition timing
        # ----------------------------------------------------

        if (
            current_time
            - last_recognition_time
            >= RECOGNITION_INTERVAL
        ):

            if (
                current_time
                - last_attendance_time
                >= ATTENDANCE_COOLDOWN
            ):

                last_recognition_time = current_time

                print(
                    "\n"
                    + "-" * 60
                )

                print(
                    "Running face recognition..."
                )

                student_id, name, distance = recognize_student(

                    frame,

                    students
                )

                # ------------------------------------------------
                # Recognized
                # ------------------------------------------------

                if student_id is not None:

                    recognized_student = (
                        student_id,
                        name
                    )

                    success_mark, result_message = (
                        mark_attendance(
                            student_id,
                            name
                        )
                    )

                    if success_mark:

                        status_message = (
                            f"Attendance Marked: "
                            f"{name}"
                        )

                        status_color = (
                            0,
                            255,
                            0
                        )

                        last_attendance_time = (
                            current_time
                        )

                    else:

                        status_message = (
                            f"{name}: "
                            f"{result_message}"
                        )

                        status_color = (
                            0,
                            255,
                            255
                        )

                # ------------------------------------------------
                # Not recognized
                # ------------------------------------------------

                else:

                    recognized_student = None

                    status_message = (
                        "Face not recognized"
                    )

                    status_color = (
                        0,
                        0,
                        255
                    )

        # ----------------------------------------------------
        # Top information area
        # ----------------------------------------------------

        cv2.rectangle(

            frame,

            (0, 0),

            (
                frame.shape[1],
                100
            ),

            (0, 0, 0),

            -1
        )

        draw_status(

            frame,

            "AI SMART ATTENDANCE",

            (255, 255, 255),

            30
        )

        draw_status(

            frame,

            status_message,

            status_color,

            68
        )

        # ----------------------------------------------------
        # Recognized student
        # ----------------------------------------------------

        if recognized_student is not None:

            student_id, name = (
                recognized_student
            )

            info = (
                f"Student: {name} | "
                f"ID: {student_id}"
            )

            cv2.putText(

                frame,

                info,

                (
                    20,
                    frame.shape[0] - 45
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.65,

                (255, 255, 255),

                2,

                cv2.LINE_AA
            )

        # ----------------------------------------------------
        # Instructions
        # ----------------------------------------------------

        cv2.putText(

            frame,

            "Press Q to quit",

            (
                20,
                frame.shape[0] - 15
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (200, 200, 200),

            1,

            cv2.LINE_AA
        )

        # ----------------------------------------------------
        # Show camera
        # ----------------------------------------------------

        cv2.imshow(

            "AI Smart Attendance",

            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            print(
                "\nStopping attendance..."
            )

            break

        if key == 27:  # ESC

            print(
                "\nESC pressed. Stopping..."
            )

            break

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    print(
        "\nWebcam closed."
    )

    print(
        "Attendance system stopped."
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        run_attendance()

    except KeyboardInterrupt:

        print(
            "\nAttendance system stopped."
        )

        cv2.destroyAllWindows()

    except Exception as error:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "UNEXPECTED ERROR"
        )

        print(
            "=" * 70
        )

        print(error)

        cv2.destroyAllWindows()

        input(
            "\nPress ENTER to close..."
        )

