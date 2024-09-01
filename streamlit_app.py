import streamlit as st

def instructions_page():
    st.title("GradeSlop")
    st.write("""
        **GradeSlop** is an LLM-based assignment submission critique system that accesses student data using the [Canvas LMS REST API](https://canvas.instructure.com/doc/api/).
        Behind the scenes, it uses the [OpenAI text generation API](https://platform.openai.com/docs/guides/text-generation) to generate critiques that *might* be helpful when grading many student submissions for a single assignment.

        To get started, use the :material/key: menu in the sidebar to provide your Canvas access token and an OpenAI API key.
        Any Canvas LMS user can generate their own access token following [these instructions](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89).
        To get an OpenAI API key, well, someone's going to have to pay. (A future version of this app might allow you to paste in an alternate text completion endpoint, bypassing OpenAI.)
             
        This app does not record your keys or log your student data. In the current design, if you close the page (ending your iteraction session), your keys are immediately lost.
    """)

def assignment_selection_page():
    st.write("assignment selection page")

def submission_selection_page():
    st.write("submission selection page")

def grading_page():
    st.write("grading page")

with st.sidebar.expander('Access keys', icon=":material/key:"):
    # TODO: use https://pypi.org/project/streamlit-local-storage/ to persist across sessions
    st.session_state.CANVAS_TOKEN = st.text_input('CANVAS_TOKEN', type="password", value=st.session_state.get('CANVAS_TOKEN',''))
    st.session_state.OPENAI_API_KEY = st.text_input('OPENAI_API_KEY', type="password", value=st.session_state.get('OPENAI_API_KEY',''))
    

st.navigation([
    st.Page(instructions_page, title="GradeSlop Overview"),
    st.Page(assignment_selection_page, title="Assignment Selection"),
    st.Page(submission_selection_page, title="Submission Selection"),
    st.Page(grading_page, title="Grading")
]).run()