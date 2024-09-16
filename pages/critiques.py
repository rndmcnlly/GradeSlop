import streamlit as st
import utils
import requests
import openai
import bs4

st.title("Critiques")

if "CANVAS_API_URL" not in st.session_state:
    utils.die("Please set the Canvas API URL in the settings.")
elif "CANVAS_ACCESS_TOKEN" not in st.session_state:
    utils.die("Please set the Canvas access token in the settings.")
elif "SELECTED_COURSE_ID" not in st.session_state:
    utils.die("Please select a course in the assignments page.")
elif "SELECTED_ASSIGNMENT_ID" not in st.session_state:
    utils.die("Please select an assignment in the assignments page.")
elif "SELECTED_USER_ID" not in st.session_state:
    utils.die("Please select a submission in the submissions page.")

students = utils.get_gradeable_students(
    st.session_state.CANVAS_API_URL,
    st.session_state.CANVAS_ACCESS_TOKEN,
    st.session_state.SELECTED_COURSE_ID,
    st.session_state.SELECTED_ASSIGNMENT_ID,
)
students_by_id = {student.id: student for student in students}

submission = utils.get_submission(
    st.session_state.CANVAS_API_URL,
    st.session_state.CANVAS_ACCESS_TOKEN,
    st.session_state.SELECTED_COURSE_ID,
    st.session_state.SELECTED_ASSIGNMENT_ID,
    st.session_state.SELECTED_USER_ID,
)

st.subheader("Submission")
st.write(f"**{students_by_id[st.session_state.SELECTED_USER_ID].display_name}**")
with st.popover("Submission details"):
    st.write(vars(submission))

st.subheader("Prompt")
if "CRITIQUE_PROMPT" not in st.session_state:
    st.session_state["CRITIQUE_PROMPT"] = "Please provide feedback on the student's submission."

prompt = st.text_area(
    "Prompt", value=st.session_state["CRITIQUE_PROMPT"], height=100
)
st.session_state["CRITIQUE_PROMPT"] = prompt

submission_body = ""

if submission.submission_type == "online_url":
    with st.spinner("Following submission link..."):
        response = requests.get(submission.url)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            submission_body = soup.get_text()
        else:
            st.warn("Failed to download submission.")
elif submission.submission_type == "online_upload":
    with st.spinner("Downloading submission attachments..."):
        for attachment in submission.attachments:
            if getattr(attachment, "content-type") == "text/html":
                if st.expander("View attachment"):
                    response = requests.get(attachment.url)
                    if response.status_code == 200:
                        file_content = response.content.decode("utf-8")[:1024]
                        submission_body += f"# {attachment.filename}\n{file_content}\n"
                    else:
                        st.warn(f"Failed to download {attachment.filename}.")
else:
    st.warning(f"Unhandled submission type: {submission.submission_type}")


with st.popover("Context"):
    st.text(submission_body)

st.subheader("Critique")

openai_client = openai.Client(api_key=st.session_state.OPENAI_API_KEY, base_url=st.session_state.OPENAI_API_URL)

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
