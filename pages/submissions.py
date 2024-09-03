import streamlit as st
import utils

st.title("Submissions")

submissions = utils.get_submissions(
    st.session_state.CANVAS_API_URL,
    st.session_state.CANVAS_ACCESS_TOKEN,
    st.session_state.SELECTED_COURSE_ID,
    st.session_state.SELECTED_ASSIGNMENT_ID,
)

students = utils.get_gradeable_students(
    st.session_state.CANVAS_API_URL,
    st.session_state.CANVAS_ACCESS_TOKEN,
    st.session_state.SELECTED_COURSE_ID,
    st.session_state.SELECTED_ASSIGNMENT_ID,
)

students_by_id = {student.id: student for student in students}

for submission in submissions:
    left,right = st.columns([1,1])
    button = left.button(f"{submission.user_id} ({students_by_id[submission.user_id].display_name})", type="primary")
    right.write(f"{submission.workflow_state}")
    if button:
        st.session_state.SELECTED_USER_ID = submission.user_id
        st.switch_page("pages/critiques.py")

if st.button("Reload Canvas data"):
    utils.get_submissions.clear()
    utils.get_gradeable_students.clear()
    st.rerun()