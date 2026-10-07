@"

\# AI Smart Attendance System



An AI-powered smart attendance system that uses \*\*face recognition\*\* to automatically identify students and record their attendance.



\## Features



\- Face recognition-based student identification

\- Automated attendance marking

\- Real-time camera-based recognition

\- Student registration using face images

\- Attendance records stored in CSV format

\- User-friendly graphical interface

\- Integration of OpenCV and DeepFace

\- Student information management

\- Attendance tracking and record management



\## Technologies Used



\- \*\*Python\*\* – Core programming language

\- \*\*OpenCV\*\* – Computer vision and camera processing

\- \*\*DeepFace\*\* – Face recognition and facial analysis

\- \*\*Tkinter\*\* – Graphical user interface

\- \*\*CSV\*\* – Student and attendance data storage

\- \*\*NumPy\*\* – Numerical and image-processing operations

\- \*\*Computer Vision\*\* – Real-time face detection and recognition

\- \*\*Face Recognition\*\* – Student identification and attendance automation



\## How It Works



1\. Student face images are stored in the `Images/` directory.

2\. Student details are maintained in `data/students.csv`.

3\. The application accesses the camera using OpenCV.

4\. DeepFace is used for face recognition.

5\. The recognized student is matched with the registered student data.

6\. Attendance is recorded automatically.

7\. Attendance information can be maintained and reviewed through the application.



\## Project Structure



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

&#x20;   └── students.csv

