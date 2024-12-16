import streamlit as st
from frontend.services.api import APIClient
from typing import List, Dict
import base64

def handle_image_upload(index):
    uploaded_file = st.file_uploader(f"Image for question {index}", key=f"q{index}_image")
    if not uploaded_file:
        return None
    
    try:
        file_bytes = uploaded_file.getvalue()
        encoded = base64.b64encode(file_bytes)
        return encoded.decode('utf-8')  # Ensure we return the decoded string
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def create_question_form(index):
    # Get question text
    question_text = st.text_area(f"Question {index + 1}", key=f"q{index}_text")
    if not question_text:
        return None
        
    # Get points
    points = st.number_input(
        "Points",
        min_value=1,
        max_value=10,
        value=1,
        key=f"q{index}_points"
    )
    
    # Get number of choices
    num_choices = st.number_input(
        "Number of Choices",
        min_value=2,
        max_value=5,
        value=2,
        key=f"q{index}_num_choices"
    )
    
    # Collect choices
    choices = []
    for i in range(int(num_choices)):
        choice_text = st.text_input(f"Choice {i+1}", key=f"q{index}_choice_{i}")
        is_correct = st.checkbox(f"Is Correct Answer", key=f"q{index}_correct_{i}")
        if choice_text:
            choices.append({"text": choice_text, "is_correct": is_correct})
    
    # Only return if we have valid data
    if question_text and len(choices) >= 2:
        return {
            "text": question_text,
            "points": points,
            "choices": choices
        }
    return None

def quiz_list():
    st.header("My Quizzes")
    
    api = APIClient()
    response = api.get(
        'quizzes/',
        headers={'Authorization': f'Token {st.session_state.token}'}
    )
    
    if response and response.status_code == 200:
        quizzes = response.json()
        if not quizzes:
            st.info("You haven't created any quizzes yet.")
        else:
            for quiz in quizzes:
                with st.expander(quiz['title'], expanded=False):
                    st.write(quiz['description'])
                    st.write(f"Questions: {len(quiz['questions'])}")
                    if st.button("Edit", key=f"edit_{quiz['id']}"):
                        st.session_state["edit_quiz_id"] = quiz['id']
                    if st.button("Delete", key=f"delete_{quiz['id']}"):
                        if delete_quiz(quiz['id']):
                            st.rerun()

    if st.button("🔄 Refresh"):
        st.rerun()

def validate_quiz_data(title: str, description: str, questions: List[Dict]) -> tuple:
    """Validate quiz data before submission"""
    if not title.strip():
        return False, "Quiz title is required"
    if not description.strip():
        return False, "Quiz description is required"
    if not questions:
        return False, "At least one question is required"
    
    for q in questions:
        if not q['text'].strip():
            return False, "Question text cannot be empty"
        if len(q['choices']) < 2:
            return False, "Each question must have at least 2 choices"
        if not any(c['is_correct'] for c in q['choices']):
            return False, "Each question must have at least 1 correct answer"
    
    return True, None

def quiz_create_form():
    with st.form(key="quiz-form", clear_on_submit=True):
        st.markdown('<div data-testid="quiz-form">', unsafe_allow_html=True)
        st.subheader("Create New Quiz")
        
        # Basic quiz info
        title = st.text_input("Quiz Title", key="quiz-title")
        description = st.text_area("Quiz Description", key="quiz-description")
        quiz_image = handle_image_upload("quiz")  # Pass "quiz" as identifier
        
        # Questions section
        st.subheader("Questions")
        num_questions = st.number_input(
            "Number of Questions",
            min_value=1,
            max_value=10,
            value=1
        )
        
        questions = []
        for i in range(num_questions):
            question = create_question_form(i)
            if question:
                questions.append(question)
        
        submitted = st.form_submit_button("Create Quiz")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submitted:
            # Validate quiz data
            is_valid, error = validate_quiz_data(title, description, questions)
            if not is_valid:
                st.error(error)
                return
            
            # Prepare quiz data
            quiz_data = {
                'title': title,
                'description': description,
                'image': quiz_image,
                'questions': questions
            }
            
            # Submit to API
            api = APIClient()
            response = api.post(
                'quizzes/',
                data=quiz_data,
                headers={'Authorization': f'Token {st.session_state.token}'}
            )
            
            if response is None:
                return
                
            if response.status_code == 201:
                st.success("Quiz created successfully!")
                st.session_state["show_create_form"] = False
                st.rerun()
            else:
                error_msg = response.json().get('error', 'Unknown error')
                st.error(f"Failed to create quiz: {error_msg}")

def delete_quiz(quiz_id: int) -> bool:
    """Delete a quiz"""
    if st.warning("Are you sure you want to delete this quiz?"):
        api = APIClient()
        response = api.delete(
            f'quizzes/{quiz_id}/',
            headers={'Authorization': f'Token {st.session_state.token}'}
        )
        if response and response.status_code == 204:
            st.success("Quiz deleted successfully!")
            return True
        else:
            st.error("Failed to delete quiz")
            return False
    return False