import streamlit as st
import openai
import canvasapi

@st.cache_resource(ttl=3600, show_spinner="Getting OpenAI models list...")
def get_models(base_url, api_key):
    return openai.Client(api_key=api_key, base_url=base_url).models.list().data

@st.cache_resource(ttl=3600, show_spinner="Getting courses...")
def get_courses(api_url, api_key):
    return list(canvasapi.Canvas(api_url, api_key).get_courses())

@st.cache_resource(ttl=3600, show_spinner="Getting user...")
def get_user(api_url, api_key):
    return canvasapi.Canvas(api_url, api_key).get_current_user()

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