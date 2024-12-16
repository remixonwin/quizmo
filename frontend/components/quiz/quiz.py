import streamlit as st
from frontend.services.api import APIClient
from typing import List, Dict
import base64

def handle_image_upload(question_number) -> str:
    """Handle image upload and convert to base64"""
    uploaded_file = st.file_uploader("Upload Image (optional)", 
                                    type=['png', 'jpg', 'jpeg'],
                                    key=f"image_upload_{question_number}")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

def create_question_form(index: int) -> Dict:
    """Create a form for a single question"""
    with st.expander(f"Question {index + 1}", expanded=True):
        question_text = st.text_area(f"Question Text", key=f"q{index}_text")
        points = st.number_input(f"Points", min_value=1, value=1, key=f"q{index}_points")
        image = handle_image_upload(index)
        
        choices = []
        st.write("Choices (minimum 2, at least 1 correct)")
        for i in range(4):  # Allow up to 4 choices
            col1, col2 = st.columns([3, 1])
            with col1:
                choice_text = st.text_input(
                    f"Choice {i+1}", 
                    key=f"q{index}_c{i}_text"
                )
            with col2:
                is_correct = st.checkbox(
                    "Correct", 
                    key=f"q{index}_c{i}_correct"
                )
            if choice_text:
                choices.append({
                    'text': choice_text,
                    'is_correct': is_correct
                })

        return {
            'text': question_text,
            'points': points,
            'image': image,
            'choices': choices
        } if question_text and len(choices) >= 2 else None

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