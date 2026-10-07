# AI Smart Attendance System

## Project Overview

The **AI Smart Attendance System** is an automated attendance management application that uses **Artificial Intelligence and Computer Vision** to identify registered students through facial recognition and record their attendance.

The system uses **OpenCV** for image and camera processing and **DeepFace** for face recognition. Student information and attendance records are maintained using CSV files, while **Tkinter** provides the graphical user interface.

The main objective of this project is to reduce manual attendance work, improve attendance accuracy, and provide a simple automated solution for student attendance management.

---

## Key Features

* Automated face recognition-based attendance
* Real-time webcam-based student identification
* Student registration and face image management
* Automatic attendance recording
* CSV-based student and attendance data storage
* Graphical user interface using Tkinter
* Face detection and image processing using OpenCV
* Facial recognition using DeepFace
* Student attendance tracking
* Attendance record management

---

## Technologies Used

| Technology       | Purpose                                             |
| ---------------- | --------------------------------------------------- |
| Python           | Core application development                        |
| OpenCV           | Computer vision, webcam access and image processing |
| DeepFace         | Facial recognition and verification                 |
| Tkinter          | Graphical user interface                            |
| CSV              | Student and attendance data storage                 |
| NumPy            | Numerical and image-processing operations           |
| Computer Vision  | Face detection and recognition                      |
| Face Recognition | Student identification                              |

---

## System Workflow

```text
Student Face Image
        |
        v
   Image Storage
        |
        v
   Webcam Capture
        |
        v
  Face Detection
        |
        v
 DeepFace Recognition
        |
        v
 Student Identification
        |
        v
 Attendance Verification
        |
        v
 Attendance Record
        |
        v
      CSV File
```

---

## How the System Works

1. Student details are registered in the system.
2. The student's face image is stored in the `Images/` directory.
3. Student information is maintained in `data/students.csv`.
4. The application accesses the webcam using OpenCV.
5. The system detects faces from the camera feed.
6. DeepFace performs facial recognition against the registered student images.
7. When a registered student is identified, the corresponding student information is retrieved.
8. Attendance is recorded automatically.
9. Attendance information is stored for future reference.

---

## Project Structure

```text
AI-Smart-Attendance-New/
│
├── main.py
├── frontend.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── Images/
│   ├── Student face images
│   └── Face recognition model files
│
└── data/
    └── students.csv
```

---

## Student Data

Student information is stored in:

```text
data/students.csv
```

The file contains the following fields:

```text
StudentID,Name,Image
```

Example:

```text
StudentID,Name,Image
101,Alice,101_Alice.jpg
102,Bhoomika,102_Bhoomika.jpg
103,Charles,103_Charles.jpg
```

The `Image` field contains the filename of the corresponding student face image located inside the `Images/` directory.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/bhoomikas702-art/AI-Smart-Attendance.git
```

### 2. Navigate to the Project Directory

```bash
cd AI-Smart-Attendance
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

Run the main application:

```bash
python main.py
```

If the frontend is designed to run separately:

```bash
python frontend.py
```

Make sure that the webcam is connected and the required student images are available in the `Images/` directory.

---

## Requirements

* Python 3.x
* Webcam
* OpenCV
* DeepFace
* NumPy
* Tkinter
* Required packages listed in `requirements.txt`
* Registered student face images

---

## Important Project Files

### `main.py`

Contains the main attendance and face-recognition functionality.

### `frontend.py`

Provides the graphical user interface for interacting with the application.

### `requirements.txt`

Contains the Python dependencies required to run the project.

### `data/students.csv`

Stores registered student information.

### `Images/`

Contains student face images and required face-recognition model files.

---

## Applications

The system can be used for:

* College attendance management
* School attendance management
* Classroom attendance automation
* Training institute attendance
* Small-scale organization attendance tracking

---

## Advantages

* Reduces manual attendance work
* Saves time during attendance collection
* Provides automated student identification
* Reduces duplicate or repeated attendance entries
* Maintains digital attendance records
* Provides a simple graphical interface
* Uses computer vision for real-time recognition

---

## Limitations

* Requires a working webcam
* Recognition performance can depend on image quality and lighting
* Registered student images are required
* Performance may vary depending on hardware and environment

---

## Future Enhancements

Possible future improvements include:

* Database integration using MySQL or PostgreSQL
* Cloud-based attendance management
* Attendance reports and analytics
* Email or notification support
* Multiple classroom or camera support
* Improved authentication and security
* Mobile application integration
* Advanced face-recognition models
* Exporting attendance reports to Excel or PDF

---

## Privacy and Security

Face images used for testing and demonstration should be sample or dummy images when the project is published publicly.

Personal photographs or sensitive biometric information should not be exposed in a public repository without appropriate authorization.

---

## Author

**Bhoomika**

## Project

**AI Smart Attendance System**

## Repository

[AI-Smart-Attendance](https://github.com/bhoomikas702-art/AI-Smart-Attendance)
