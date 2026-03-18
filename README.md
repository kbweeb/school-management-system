# Group 23 Student Record Management System

Python backend + Streamlit frontend implementation of:

> Student Record Management System  
> (Add, update, delete, search, sort, display student academic records)

## Scope Covered

### Data Structures

- `list` (array-like storage for records)
- `dict` (hash table mapping `student_id -> index`)

### Algorithms

- Linear Search
- Binary Search
- Sorting:
  - Bubble Sort
  - Insertion Sort
  - Merge Sort

### Functional Specifications

- Add new student (`ID`, `name`, `course`, `CWA/GPA`)
- Update student records
- Delete student records
- Search by ID or name
- Sort students by CWA or name
- Display all records

## Project Structure

- `app.py` -> Streamlit interface
- `backend/student_records.py` -> backend logic, data structures, and algorithms
- `data/student_records.json` -> local storage file (created at runtime)

## Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
streamlit run app.py
```
