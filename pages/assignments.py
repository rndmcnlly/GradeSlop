import streamlit as st
import utils

st.title("Assignments")

if "CANVAS_API_URL" not in st.session_state:
    utils.die("Please set the Canvas API URL in the settings.")
elif "CANVAS_ACCESS_TOKEN" not in st.session_state:
    utils.die("Please set the Canvas access token in the settings.")

courses = utils.get_courses(st.session_state.CANVAS_API_URL, st.session_state.CANVAS_ACCESS_TOKEN)

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

assignments = utils.get_assignments(st.session_state.CANVAS_API_URL, st.session_state.CANVAS_ACCESS_TOKEN, st.session_state.SELECTED_COURSE_ID)

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

st.write("View submissions for this assignment:")
if st.button(str(assignment), type="primary"):
    st.switch_page("pages/submissions.py")

if st.button("Reload Canvas data"):
    utils.get_courses.clear()
    utils.get_assignments.clear()
    st.rerun()