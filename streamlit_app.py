import streamlit as st
import utils
import re


def overview_page():
    st.title("GradeSlop")
    st.write(
        """
        **GradeSlop** is an LLM-based assignment submission critique system that accesses student data using the [Canvas LMS REST API](https://canvas.instructure.com/doc/api/).
        Behind the scenes, it uses the [OpenAI text generation API](https://platform.openai.com/docs/guides/text-generation) to generate critiques that *might* be helpful when grading many student submissions for a single assignment.

        To get started, provide your Canvas access token and an OpenAI API key using the sidebar menu.

        **Note**:     
        This app does *not* record your keys on the server or record your student data in any database. Access keys are only stored in your browser. 
    """
    )


def canvas_setup_page():

    st.header("Canvas Access Token")
    utils._prompt_key("CANVAS_ACCESS_TOKEN", type="password")
    utils._prompt_key("CANVAS_API_URL", default="https://canvas.ucsc.edu")

    canvas_client = utils.get_canvas_client(
        st.session_state.CANVAS_ACCESS_TOKEN, st.session_state.CANVAS_API_URL
    )
    if canvas_client:
        st.success("Canvas API access is available.")
        st.write(f"You are **{canvas_client.get_current_user()}**.")
    else:
        st.error("Canvas API access is unavailable. Check your access token.")


def openai_setup_page():
    st.header("OpenAI")
    utils._prompt_key("OPENAI_API_KEY", type="password")
    utils._prompt_key("OPENAI_BASE_URL", default="https://api.openai.com/v1")

    openai_client = utils.get_openai_client(
        st.session_state.OPENAI_API_KEY, st.session_state.OPENAI_BASE_URL
    )
    if openai_client:
        st.success("OpenAI API access is available.")
        md = "Available GPT models:\n"
        md += "\n".join(
            f"- {model.id}"
            for model in openai_client.models.list().data
            if model.id.startswith("gpt-")
        )
        st.write(md)
    else:
        st.error("OpenAI models unavailable. Check your API key.")


with st.sidebar:
    if url := st.text_input(
        "Canvas URL", help="A course, assignment, submission, or SpeedGrader URL"
    ):

        if match := re.match(
            r".*/courses/(\d+)/gradebook/speed_grader\?assignment_id=(\d+)&student_id=(\d+)",
            url,
        ):
            if st.button("Critique this submission"):
                st.session_state["SELECTED_COURSE_ID"] = match.group(1)
                st.session_state["SELECTED_ASSIGNMENT_ID"] = match.group(2)
                st.session_state["SELECTED_USER_ID"] = match.group(3)
                st.switch_page("pages/critiques.py")
        elif match := re.match(
            r".*/courses/(\d+)/assignments/(\d+)/submissions/(\d+)", url
        ):
            if st.button("Critique this submission"):
                st.session_state["SELECTED_COURSE_ID"] = match.group(1)
                st.session_state["SELECTED_ASSIGNMENT_ID"] = match.group(2)
                st.session_state["SELECTED_USER_ID"] = match.group(3)
                st.switch_page("pages/critiques.py")
        elif match := re.match(r".*/courses/(\d+)/assignments/(\d+)", url):
            if st.button("View this assignment"):
                st.session_state["SELECTED_COURSE_ID"] = match.group(1)
                st.session_state["SELECTED_ASSIGNMENT_ID"] = match.group(2)
                st.switch_page("pages/submissions.py")
        elif match := re.match(r".*/courses/(\d+)", url):
            if st.button("View this course"):
                st.session_state["SELECTED_COURSE_ID"] = match.group(1)
                st.switch_page("pages/assignments.py")
        else:
            st.error("Invalid URL")


st.navigation(
    [
        st.Page(overview_page, title="Overview", url_path="home", default=True),
        st.Page(canvas_setup_page, title="Canvas Access Token", url_path="canvas"),
        st.Page(openai_setup_page, title="OpenAI API Key", url_path="openai"),
        st.Page("pages/assignments.py", title="Assignments", url_path="assignments"),
        st.Page("pages/submissions.py", title="Submissions", url_path="submissions"),
        st.Page("pages/critiques.py", title="Critiques", url_path="critiques"),
    ]
).run()
