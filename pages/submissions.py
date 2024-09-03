import canvasapi.exceptions
import canvasapi.submission
import streamlit as st
import utils
import canvasapi

st.title("Submissions")

canvas_client = utils.get_current_canvas_client()
if not canvas_client:
    st.error("Canvas API not configured.")
    st.stop()

try:
    course = canvas_client.get_course(st.session_state["SELECTED_COURSE_ID"])
    assignment = course.get_assignment(st.session_state["SELECTED_ASSIGNMENT_ID"])
except Exception as e:
    st.switch_page("pages/assignments.py")

st.header(course)
st.subheader(assignment)
students = assignment.get_gradeable_students()
submissions = assignment.get_submissions()

students_by_id = {student.id: student for student in students}

for submission in submissions:
    left,right = st.columns([1,1])
    button = left.button(f"{submission.user_id} ({students_by_id[submission.user_id].display_name})", type="primary")
    right.write(f"{submission.workflow_state}")
    if button:
        st.session_state["SELECTED_USER_ID"] = submission.user_id
        st.switch_page("pages/critiques.py")