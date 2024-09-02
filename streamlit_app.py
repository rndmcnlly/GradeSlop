import streamlit as st
import openai
import canvasapi

@st.cache_resource(ttl=60)
def get_openai_client(api_key, base_url):
    if not api_key:
        return None
    try:
        client = openai.Client(api_key=api_key, base_url=base_url)
        models = client.models.list()
        assert models.data
        return client
    except openai.AuthenticationError as e:
        return None
    except openai.APIConnectionError as e:
        return None
    
@st.cache_resource(ttl=60)
def get_canvas_client(api_key, apu_url):
    if not api_key:
        return None
    try:
        return canvasapi.Canvas(apu_url, api_key)
    except canvasapi.exceptions.InvalidAccessToken as e:
        return None

def instructions_page():
    st.title("GradeSlop")
    st.write("""
        **GradeSlop** is an LLM-based assignment submission critique system that accesses student data using the [Canvas LMS REST API](https://canvas.instructure.com/doc/api/).
        Behind the scenes, it uses the [OpenAI text generation API](https://platform.openai.com/docs/guides/text-generation) to generate critiques that *might* be helpful when grading many student submissions for a single assignment.

        To get started, use the :material/key: menu in the sidebar to provide your Canvas access token and an OpenAI API key.
        Any Canvas LMS user can generate their own access token following [these instructions](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89).
        To get an OpenAI API key, well, someone's going to have to pay.
             
        This app does not record your keys or log your student data. In the current design, if you close the page (ending your iteraction session), your keys are immediately lost.
    """)

def assignment_selection_page():
    st.title("Assignment Selection")

    canvas_client = get_canvas_client(st.session_state.CANVAS_ACCESS_TOKEN, st.session_state.CANVAS_API_URL)
    if not canvas_client:
        st.error("Canvas LMS unavailable. Check your access token.")
        st.stop()
    
    courses = canvas_client.get_courses()
    courses_by_name = {str(course): course for course in courses}
    course_name = st.selectbox("Select one of your courses", list(courses_by_name.keys()))
    course = courses_by_name.get(course_name, None)

    if not course:
        st.error("Select a valid course above.")
        st.stop()
    
    assignments = course.get_assignments()
    assignment_by_name = {str(assignment): assignment for assignment in assignments}
    assignment_name = st.selectbox("Select an assignment", list(assignment_by_name.keys()))
    assignment = assignment_by_name.get(assignment_name, None)
    if not assignment:
        st.error("Select a valid assignment above.")
        st.stop()

    st.success(str(assignment))

def submission_selection_page():
    st.write("submission selection page")

def grading_page():
    st.write("grading page")

with st.sidebar.expander('Access keys', icon=":material/key:", expanded=False):
    # TODO: use https://pypi.org/project/streamlit-local-storage/ to persist across sessions
    st.header("Canvas LMS")
    st.session_state.CANVAS_ACCESS_TOKEN = st.text_input('CANVAS_ACCESS_TOKEN', type="password", value=st.session_state.get('CANVAS_ACCESS_TOKEN',''))
    st.session_state.CANVAS_API_URL = st.text_input('CANVAS_API_URL', value=st.session_state.get('CANVAS_API_URL','https://canvas.ucsc.edu'))

    canvas_client = get_canvas_client(st.session_state.CANVAS_ACCESS_TOKEN, st.session_state.CANVAS_API_URL)
    if canvas_client:
        st.success(f"Canvas LMS available.")
    else:
        st.error("Canvas LMS unavailable. Check your access token.")

    st.header("OpenAI")
    st.session_state.OPENAI_API_KEY = st.text_input('OPENAI_API_KEY', type="password", value=st.session_state.get('OPENAI_API_KEY',''))
    st.session_state.OPENAI_BASE_URL = st.text_input('OPENAI_BASE_URL', value=st.session_state.get('OPENAI_BASE_URL','https://api.openai.com/v1'))
    
    openai_client = get_openai_client(st.session_state.OPENAI_API_KEY, st.session_state.OPENAI_BASE_URL)
    if openai_client:
        st.success("OpenAI models available.")
    else:
        st.error("OpenAI models unavailable. Check your API key.")
    
st.navigation([
    st.Page(instructions_page, title="GradeSlop Overview"),
    st.Page(assignment_selection_page, title="Assignment Selection"),
    st.Page(submission_selection_page, title="Submission Selection"),
    st.Page(grading_page, title="Grading")
]).run()