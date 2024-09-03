import streamlit as st
import openai
import canvasapi
from streamlit_local_storage import LocalStorage

ls = LocalStorage()

def _restore_local_state(name):
    if item := ls.getItem(name):
        st.session_state[name] = item

def _prompt_key(name, *, default="", type="default"):
    local_default = ls.getItem(name)
    if local_default:
        use_default = local_default
    else:
        use_default = default
    st.session_state[name] = st.text_input(
        name, type=type, value=st.session_state.get(name, use_default)
    )

    ls.setItem(name, st.session_state[name], key="persist_" + name)

    def on_click():
        ls.deleteItem(name, key="delete_" + name)
        del st.session_state[name]

    if st.session_state[name] != default:
        st.write(
            "This setting is saved in your browser's [`localStorage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) system to persist the data across sessions."
        )
        st.button(
            f":material/delete: Forget {name}",
            on_click=on_click,
            use_container_width=True,
            key="delete_" + name,
        )

@st.cache_resource(ttl=60)
def get_canvas_client(api_key, api_url):
    if not api_key:
        return None
    try:
        client = canvasapi.Canvas(api_url, api_key)
        user = client.get_current_user()
        return client
    except canvasapi.exceptions.InvalidAccessToken as e:
        return None


def get_current_canvas_client():
    try:
        _restore_local_state("CANVAS_ACCESS_TOKEN")
        _restore_local_state("CANVAS_API_URL")
        return get_canvas_client(
            st.session_state.CANVAS_ACCESS_TOKEN, st.session_state.CANVAS_API_URL
        )
    except AttributeError:
        st.write("Canvas API not configured.")
        st.stop()


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


def get_current_openai_client():
    try:
        _restore_local_state("OPENAI_API_KEY")
        _restore_local_state("OPENAI_BASE_URL")
        return get_openai_client(
            st.session_state.OPENAI_API_KEY, st.session_state.OPENAI_BASE_URL
        )
    except AttributeError:
        st.switch_page("openai")

@st.cache_resource(ttl=3600, show_spinner="Getting courses...")
def get_courses(api_url, api_key):
    return list(canvasapi.Canvas(api_url, api_key).get_courses())

@st.cache_resource(ttl=3600, show_spinner="Getting assignments...")
def get_assignments(api_url, api_key, course_id):
    return list(canvasapi.Canvas(api_url, api_key).get_course(course_id).get_assignments())

@st.cache_resource(ttl=3600, show_spinner="Getting submissions...")
def get_submissions(api_url, api_key, course_id, assignment_id):
    course = canvasapi.Canvas(api_url, api_key).get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    return list(assignment.get_submissions())

@st.cache_resource(ttl=3600, show_spinner="Getting gradeable students...")
def get_gradeable_students(api_url, api_key, course_id, assignment_id):
    course = canvasapi.Canvas(api_url, api_key).get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    return list(assignment.get_gradeable_students())

@st.cache_resource(ttl=3600, show_spinner="Getting submission...")
def get_submission(api_url, api_key, course_id, assignment_id, user_id):
    course = canvasapi.Canvas(api_url, api_key).get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    return assignment.get_submission(user_id)