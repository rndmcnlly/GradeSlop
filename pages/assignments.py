import streamlit as st
import utils
import re

st.title("Assignments")

canvas_client = utils.get_current_canvas_client()
if not canvas_client:
    st.error("Canvas API not configured.")
    st.stop()

with st.spinner("Loading your courses..."):
    courses = canvas_client.get_courses()

courses_by_id = {course.id: course for course in courses}
course_ids = list(courses_by_id.keys())
try:
    course_index = course_ids.index(int(st.session_state["SELECTED_COURSE_ID"]))
except:
    course_index = 0

course_id = st.selectbox(
    "Select one of your courses",
    course_ids,
    format_func=lambda x: str(courses_by_id[x]),
    index=course_index,
)
st.session_state["SELECTED_COURSE_ID"] = course_id
course = courses_by_id.get(course_id)

if not course:
    st.error("Select a valid course above.")
    st.stop()

with st.spinner("Loading assignments for that course..."):
    assignments = course.get_assignments()

assignments_by_id = {assignment.id: assignment for assignment in assignments}
assignment_ids = list(assignments_by_id.keys())
try:
    assignent_index = assignment_ids.index(
        int(st.session_state["SELECTED_ASSIGNMENT_ID"])
    )
except:
    assignent_index = 0
assignment_id = st.selectbox(
    "Select an assignment for that course",
    assignment_ids,
    format_func=lambda x: str(assignments_by_id[x]),
    index=assignent_index,
)
st.session_state["SELECTED_ASSIGNMENT_ID"] = assignment_id
assignment = assignments_by_id.get(assignment_id)

if not assignment:
    st.error("Select a valid assignment above.")
    st.stop()

st.write(f"Selected assignment: **{assignment}**")
if st.button("View submissions", type="primary"):
    st.switch_page("pages/submissions.py")
