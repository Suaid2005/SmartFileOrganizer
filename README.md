# Smart File Organizer

A Python-based desktop application developed as a collaborative team project for the **Operating Systems** course at **Presidency University, Bengaluru**.

Smart File Organizer simplifies file management by automatically categorizing files into organized folders through a modern graphical user interface.

## Project Overview

Managing large numbers of files manually can be time-consuming and confusing. Smart File Organizer addresses this problem by scanning a selected folder, identifying file types, and organizing them into meaningful categories.

Users can preview the proposed organization before confirming file operations, making file management easier and more structured.

## Features

- **Smart File Categorization** – Identifies file types using their extensions.
- **Folder Scanning** – Scans selected folders and analyzes their contents.
- **Organization Preview** – Preview the proposed file arrangement before applying changes.
- **Automatic Organization** – Moves files into automatically created category folders.
- **File Explorer** – Browse and search files through the application.
- **Storage Analyzer** – View storage information and file category breakdowns.
- **Undo Support** – Reverse the most recent organization operation during the current application session.
- **Modern Graphical Interface** – A desktop interface built using CustomTkinter.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| CustomTkinter | Graphical user interface |
| Pillow | Image handling |
| OS and pathlib | File and directory operations |
| shutil | File movement |
| Git and GitHub | Version control and source hosting |

## Project Structure

```text
SmartFileOrganizer/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── organizer/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── file_manager.py
│   └── history.py
│
└── ui/
    ├── __init__.py
    └── dashboard.py
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip package manager
- Windows, macOS, or Linux with a supported Python and Tkinter environment

### 1. Clone the repository

```bash
git clone https://github.com/Suaid2005/SmartFileOrganizer.git
```

### 2. Navigate to the project directory

```bash
cd SmartFileOrganizer
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

## How to Use

1. Launch Smart File Organizer.
2. Select the folder you want to organize.
3. Scan the folder to analyze its contents.
4. Review the proposed file categories.
5. Confirm the organization operation.
6. Browse the organized files through the application.

**Note:** Always test with a separate sample folder before organizing important personal files. Organization moves files from their original locations.

## Operating System Concepts

This project demonstrates practical applications of Operating Systems concepts, including:

- File system management
- File and directory handling
- Directory traversal
- File classification
- File movement and manipulation
- Basic file operation history

## Team Members

This project was collaboratively developed by the following team members:

1. **MUHAMMAD SUAID**
2. **GHATAKARI KRISHNA MAHESH**
3. **CHUKKA BHANU PRAKASH**
4. **KONDURU VISHAL VERMA**

All team members are credited for their shared contribution to the project.

## Academic Details

| Detail | Information |
|---|---|
| Institution | Presidency University, Bengaluru |
| Programme | B.Tech Computer Science and Technology – DevOps |
| Subject | Operating Systems |
| Project | Smart File Organizer |
| Project Type | Collaborative Team Project |

## Repository

**GitHub:** [SmartFileOrganizer](https://github.com/Suaid2005/SmartFileOrganizer)

## Acknowledgements

We would like to express our appreciation to our institution and the faculty members of the Computer Science and Technology – DevOps programme for providing the opportunity to develop this project as part of our Operating Systems coursework.

---

**Smart File Organizer**  
*Making file management simpler, smarter, and more organized.*

Developed collaboratively by the Smart File Organizer Team  
Presidency University, Bengaluru