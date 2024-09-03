import streamlit as st
import utils
import requests
import openai

st.title("Critiques")

canvas_client = utils.get_current_canvas_client()
if not canvas_client:
    st.error("Canvas API not configured.")
    st.stop()

try:
    course = canvas_client.get_course(st.session_state["SELECTED_COURSE_ID"])
    assignment = course.get_assignment(st.session_state["SELECTED_ASSIGNMENT_ID"])
    submission = assignment.get_submission(st.session_state["SELECTED_USER_ID"])
except Exception as e:
    st.switch_page("pages/submissions.py")
    
# user = client.get_user(st.session_state["SELECTED_USER_ID"])

# st.subheader(user)

st.markdown(
    f"[SpeedGrader link](https://canvas.ucsc.edu/courses/{course.id}/gradebook/speed_grader?assignment_id={assignment.id}&student_id={submission.user_id})"
)

submission_body = ""

for attachment in submission.attachments:
    if getattr(attachment, "content-type") == "text/html":
        if st.expander("View attachment"):
            response = requests.get(attachment.url)
            if response.status_code == 200:
                file_content = response.content.decode("utf-8")
                submission_body += f"{file_content}\n"
                with st.popover(attachment.filename):
                    st.text(file_content)
            else:
                st.warn(f"Failed to download {attachment.filename}.")

st.subheader("Prompt")
if "CRITIQUE_PROMPT" not in st.session_state:
    st.session_state["CRITIQUE_PROMPT"] = "Please provide feedback on the student's submission."

prompt = st.text_area(
    "Prompt", value=st.session_state["CRITIQUE_PROMPT"], height=100
)
st.session_state["CRITIQUE_PROMPT"] = prompt

st.subheader("Critique")

openai_client = utils.get_current_openai_client()
if not openai_client:
    st.error("OpenAI API not configured.")
    st.stop()

with st.chat_message("assistant"):
        st.write_stream(
            openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": submission_body},
                ],
                stream=True,
            )
        )
