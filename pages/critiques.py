import streamlit as st
import utils
import requests
import openai

st.title("Critiques")


submission = utils.get_submission(
    st.session_state.CANVAS_API_URL,
    st.session_state.CANVAS_ACCESS_TOKEN,
    st.session_state.SELECTED_COURSE_ID,
    st.session_state.SELECTED_ASSIGNMENT_ID,
    st.session_state.SELECTED_USER_ID,
)

submission_body = ""

for attachment in submission.attachments:
    if getattr(attachment, "content-type") == "text/html":
        if st.expander("View attachment"):
            response = requests.get(attachment.url)
            if response.status_code == 200:
                file_content = response.content.decode("utf-8")[:1024]
                submission_body += f"# {attachment.filename}\n{file_content}\n"
            else:
                st.warn(f"Failed to download {attachment.filename}.")

st.subheader("Prompt")
if "CRITIQUE_PROMPT" not in st.session_state:
    st.session_state["CRITIQUE_PROMPT"] = "Please provide feedback on the student's submission."

prompt = st.text_area(
    "Prompt", value=st.session_state["CRITIQUE_PROMPT"], height=100
)
st.session_state["CRITIQUE_PROMPT"] = prompt

with st.popover("Submission body"):
    st.text(submission_body)

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
