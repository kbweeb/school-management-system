from __future__ import annotations

import streamlit as st

from backend.student_records import StudentRecordSystem


st.set_page_config(page_title="Group 23 Student Records", layout="wide")
system = StudentRecordSystem()


def render_records(records: list[dict]) -> None:
    if records:
        st.dataframe(records, hide_index=True, use_container_width=True)
    else:
        st.info("No records found.")


def all_ids() -> list[int]:
    return [int(record["student_id"]) for record in system.list_students()]


def show_dashboard() -> None:
    st.header("Overview")
    records = system.list_students()
    total = len(records)
    average_cwa = round(sum(float(record["cwa"]) for record in records) / total, 2) if total else 0.0
    highest = max((float(record["cwa"]) for record in records), default=0.0)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", total)
    col2.metric("Average CWA", average_cwa)
    col3.metric("Highest CWA", highest)

    with st.expander("Project Scope Checklist", expanded=False):
        st.markdown(
            """
- Data structures: `list` + `dict` (hash table)
- Add new student (ID, name, course, GPA/CWA)
- Update student record
- Delete student record
- Search by ID or name
- Sort by CWA or name
- Display all records
- Algorithms: Linear Search, Binary Search, Bubble Sort, Insertion Sort, Merge Sort
"""
        )


def show_add_student() -> None:
    st.header("Add New Student")
    with st.form("add_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        student_id = int(col1.number_input("Student ID", min_value=1, value=1, step=1))
        cwa = float(col2.number_input("CWA / GPA", min_value=0.0, max_value=100.0, value=50.0, step=0.1))

        name = st.text_input("Student Name")
        course = st.text_input("Course / Program")

        submitted = st.form_submit_button("Add Student")
        if submitted:
            try:
                system.add_student(student_id=student_id, name=name, course=course, cwa=cwa)
                st.success("Student added successfully.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))


def show_update_delete() -> None:
    st.header("Update / Delete Student")
    student_ids = all_ids()
    if not student_ids:
        st.info("No students available yet.")
        return

    selected_id = st.selectbox("Select Student ID", options=student_ids)
    selected_record, _ = system.hash_lookup_by_id(selected_id)
    if not selected_record:
        st.error("Selected student was not found.")
        return

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Update Record")
        with st.form("update_student_form"):
            name = st.text_input("Student Name", value=str(selected_record["name"]))
            course = st.text_input("Course / Program", value=str(selected_record["course"]))
            cwa = float(
                st.number_input(
                    "CWA / GPA",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(selected_record["cwa"]),
                    step=0.1,
                )
            )
            submitted = st.form_submit_button("Update Student")
            if submitted:
                try:
                    system.update_student(student_id=selected_id, name=name, course=course, cwa=cwa)
                    st.success("Student record updated.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

    with col_right:
        st.subheader("Delete Record")
        st.warning("This action removes the student permanently.")
        if st.button("Delete Selected Student", type="secondary"):
            try:
                system.delete_student(student_id=selected_id)
                st.success("Student deleted.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))


def show_search() -> None:
    st.header("Search Student")
    search_mode = st.radio("Search By", options=["Student ID", "Name"], horizontal=True)

    if search_mode == "Student ID":
        student_id = int(st.number_input("Student ID", min_value=1, value=1, step=1))
        algorithm = st.selectbox(
            "Search Algorithm",
            options=["Linear Search", "Binary Search", "Hash Lookup (Dictionary)"],
        )
        if st.button("Run ID Search"):
            if algorithm == "Linear Search":
                record, comparisons = system.linear_search_by_id(student_id)
            elif algorithm == "Binary Search":
                record, comparisons = system.binary_search_by_id(student_id)
            else:
                record, comparisons = system.hash_lookup_by_id(student_id)

            if record:
                st.success(f"{algorithm} found 1 result with {comparisons} comparison(s).")
                render_records([record])
            else:
                st.warning(f"{algorithm} found no record after {comparisons} comparison(s).")
    else:
        query = st.text_input("Name (full or partial)")
        if st.button("Run Name Search"):
            matches, comparisons = system.linear_search_by_name(query)
            if matches:
                st.success(f"Linear Search found {len(matches)} result(s) with {comparisons} comparison(s).")
                render_records(matches)
            else:
                st.warning(f"No record matched. Comparisons: {comparisons}.")


def show_sort() -> None:
    st.header("Sort Students")
    records = system.list_students()
    if not records:
        st.info("No records available to sort.")
        return

    col1, col2, col3 = st.columns(3)
    sort_key = col1.selectbox("Sort Field", options=["name", "cwa"])
    algorithm = col2.selectbox("Algorithm", options=["bubble", "insertion", "merge"])
    order = col3.selectbox("Order", options=["Ascending", "Descending"])

    if st.button("Run Sort"):
        reverse = order == "Descending"
        sorted_records, comparisons = system.sort_students(by=sort_key, algorithm=algorithm, reverse=reverse)
        st.success(f"{algorithm.title()} Sort complete with {comparisons} comparison(s).")
        render_records(sorted_records)


def show_display_all() -> None:
    st.header("All Student Records")
    records = system.list_students()
    render_records(records)


st.title("Group 23 Student Record Management System")
st.caption("Built with Python backend + Streamlit UI, aligned to your project topic.")

menu = st.sidebar.radio(
    "Menu",
    options=[
        "Overview",
        "Add Student",
        "Update / Delete",
        "Search",
        "Sort",
        "Display All",
    ],
)

if menu == "Overview":
    show_dashboard()
elif menu == "Add Student":
    show_add_student()
elif menu == "Update / Delete":
    show_update_delete()
elif menu == "Search":
    show_search()
elif menu == "Sort":
    show_sort()
elif menu == "Display All":
    show_display_all()
