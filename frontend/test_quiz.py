
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from frontend.components.quiz import handle_image_upload, create_question_form, quiz_create_form
import base64

class TestQuizFeatures:
    @pytest.fixture
    def mock_streamlit(self):
        with patch('streamlit.file_uploader') as mock_uploader, \
             patch('streamlit.form') as mock_form, \
             patch('streamlit.text_input') as mock_text_input, \
             patch('streamlit.text_area') as mock_text_area, \
             patch('streamlit.number_input') as mock_number_input:
            
            yield {
                'uploader': mock_uploader,
                'form': mock_form,
                'text_input': mock_text_input,
                'text_area': mock_text_area,
                'number_input': mock_number_input
            }

    @pytest.fixture
    def sample_image(self):
        return base64.b64encode(b"test image data").decode()

    @pytest.fixture
    def sample_quiz_data(self):
        return {
            'title': 'Test Quiz',
            'description': 'Test Description',
            'questions': [
                {
                    'text': 'Question 1',
                    'points': 1,
                    'image': None,
                    'choices': [
                        {'text': 'Choice 1', 'is_correct': True},
                        {'text': 'Choice 2', 'is_correct': False}
                    ]
                }
            ]
        }

    def test_handle_image_upload_success(self, mock_streamlit):
        mock_file = MagicMock()
        mock_file.getvalue.return_value = b"test image data"
        mock_streamlit['uploader'].return_value = mock_file

        result = handle_image_upload("test")
        assert result == base64.b64encode(b"test image data").decode()

    def test_handle_image_upload_no_file(self, mock_streamlit):
        mock_streamlit['uploader'].return_value = None
        result = handle_image_upload("test")
        assert result is None

    @patch('frontend.services.api.APIClient')
    def test_quiz_creation_success(self, mock_api, mock_streamlit, sample_quiz_data):
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_api.return_value.post.return_value = mock_response

        # Mock form inputs
        mock_streamlit['text_input'].return_value = sample_quiz_data['title']
        mock_streamlit['text_area'].return_value = sample_quiz_data['description']
        mock_streamlit['number_input'].return_value = 1

        # Test quiz creation
        quiz_create_form()
        mock_api.return_value.post.assert_called_once()

    def test_quiz_validation(self, sample_quiz_data):
        from frontend.components.quiz import validate_quiz_data
        
        # Test valid data
        is_valid, error = validate_quiz_data(
            sample_quiz_data['title'],
            sample_quiz_data['description'],
            sample_quiz_data['questions']
        )
        assert is_valid
        assert error is None

        # Test empty title
        is_valid, error = validate_quiz_data(
            "",
            sample_quiz_data['description'],
            sample_quiz_data['questions']
        )
        assert not is_valid
        assert "title" in error.lower()

    @pytest.mark.parametrize("invalid_data", [
        {'title': '', 'description': 'Test', 'questions': []},
        {'title': 'Test', 'description': '', 'questions': []},
        {'title': 'Test', 'description': 'Test', 'questions': []}
    ])
    def test_quiz_validation_invalid_data(self, invalid_data):
        from frontend.components.quiz import validate_quiz_data
        
        is_valid, error = validate_quiz_data(
            invalid_data['title'],
            invalid_data['description'],
            invalid_data['questions']
        )
        assert not is_valid
        assert error is not None