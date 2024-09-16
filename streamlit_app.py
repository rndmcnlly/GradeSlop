import streamlit as st
import re
import extra_streamlit_components as stx


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


@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()


def make_setup_page(name, key, instructions=""):
    def setup_page():
        st.header(name)
        if key in st.session_state:
            st.write(f"We have your {name} for the current session.")
            if st.button("Forget session value"):
                del st.session_state[key]
                st.rerun()
        else:
            cookie_manager = get_cookie_manager()
            if cookie_value := cookie_manager.get(key):
                st.write(f"We have your {name} in the browser's cookies.")
                if st.button("Use cookie value", type="primary"):
                    st.session_state[key] = cookie_value
                    st.rerun()
                if st.button("Forget cookie value", type="secondary"):
                    cookie_manager.delete(key)
                    st.rerun()
            else:
                st.write(
                    f"We need your {name}. {instructions} Once you provide your details here, it will only be saved in your browser's cookies, not on the server."
                )
                if value := st.text_input(name, type="password"):
                    st.session_state[key] = value
                    cookie_manager.set(key, value)
                    st.rerun()

    return setup_page


setup_page_specs = [
    dict(
        name="Canvas Access Token",
        key="CANVAS_ACCESS_TOKEN",
        instructions="Follow [these instructions](https://community.canvaslms.com/t5/Canvas-Basics-Guide/How-do-I-manage-API-access-tokens-in-my-user-account/ta-p/615312) to generate one.",
    ),
    dict(
        name="Canvas API URL",
        key="CANVAS_API_URL",
        instructions="Typically this is something like `https://canvas.<your_institution>.edu`.",
    ),
    dict(
        name="OpenAI API Key",
        key="OPENAI_API_KEY",
        instructions="Get an API key from the [OpenAI API site](https://platform.openai.com/signup).",
    ),
    dict(
        name="OpenAI API URL",
        key="OPENAI_API_URL",
        instructions="Typically this is something like `https://api.openai.com/v1`.",
    ),
]

for spec in setup_page_specs:
    if spec["key"] in st.secrets:
        st.session_state[spec["key"]] = st.secrets[spec["key"]]

with st.sidebar:
    if url := st.text_input(
        "Canvas URL", help="A course, assignment, submission, or SpeedGrader URL"
    ):

        if match := re.match(
            r"(.*)/courses/(\d+)/gradebook/speed_grader\?assignment_id=(\d+)&student_id=(\d+)",
            url,
        ):
            if st.button("Critique this submission"):
                st.session_state["CANVAS_API_URL"] = match.group(1)
                st.session_state["SELECTED_COURSE_ID"] = match.group(2)
                st.session_state["SELECTED_ASSIGNMENT_ID"] = match.group(3)
                st.session_state["SELECTED_USER_ID"] = match.group(4)
                st.switch_page("pages/critiques.py")
        elif match := re.match(
            r"(.*)/courses/(\d+)/assignments/(\d+)/submissions/(\d+)", url
        ):
            if st.button("Critique this submission"):
                st.session_state["CANVAS_API_URL"] = match.group(1)
                st.session_state["SELECTED_COURSE_ID"] = match.group(2)
                st.session_state["SELECTED_ASSIGNMENT_ID"] = match.group(3)
                st.session_state["SELECTED_USER_ID"] = match.group(4)
                st.switch_page("pages/critiques.py")
        elif match := re.match(r"(.*)/courses/(\d+)/assignments/(\d+)", url):
            if st.button("View this assignment"):
                st.session_state["CANVAS_API_URL"] = match.group(1)
                st.session_state["SELECTED_COURSE_ID"] = match.group(2)
                st.session_state["SELECTED_ASSIGNMENT_ID"] = match.group(3)
                st.switch_page("pages/submissions.py")
        elif match := re.match(r"(.*)/courses/(\d+)", url):
            if st.button("View this course"):
                st.session_state["CANVAS_API_URL"] = match.group(1)
                st.session_state["SELECTED_COURSE_ID"] = match.group(2)
                st.switch_page("pages/assignments.py")
        else:
            st.error("Invalid URL")


page = st.navigation(
    {
        "Overview": [
            st.Page(overview_page, title="Overview", default=True),
        ],
        "Course data": [
            st.Page(
                "pages/assignments.py", title="Assignments", url_path="assignments"
            ),
            st.Page(
                "pages/submissions.py", title="Submissions", url_path="submissions"
            ),
            st.Page("pages/critiques.py", title="Critiques", url_path="critiques"),
        ],
        "Settings": [
            st.Page(
                make_setup_page(spec["name"], spec["key"], spec["instructions"]),
                title=spec["name"],
                url_path=spec["key"],
            )
            for spec in setup_page_specs if spec["key"] not in st.secrets
        ],
    }
)

page.run()
