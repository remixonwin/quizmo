import unittest
from frontend.components.quiz import create_question_form, handle_image_upload
from unittest.mock import patch, MagicMock, call

class TestQuizComponents(unittest.TestCase):
    
    @patch('frontend.components.quiz.quiz.st')
    def test_create_question_form_valid(self, mock_st):
        # Mock the form inputs
        mock_st.text_area.return_value = 'Sample Question'
        mock_st.number_input.side_effect = [1, 2]  # points, num_choices
        mock_st.text_input.side_effect = ['Choice 1', 'Choice 2']  # choice texts
        mock_st.checkbox.side_effect = [True, False]  # is_correct values
        
        # Call the function
        question = create_question_form(0)
        
        # Verify the calls were made correctly
        mock_st.text_area.assert_called_once_with('Question 1', key='q0_text')
        mock_st.number_input.assert_has_calls([
            call('Points', min_value=1, max_value=10, value=1, key='q0_points'),
            call('Number of Choices', min_value=2, max_value=5, value=2, key='q0_num_choices')
        ])
        
        # Verify the returned data structure
        self.assertIsNotNone(question)
        self.assertEqual(question, {
            'text': 'Sample Question',
            'points': 1,
            'choices': [
                {'text': 'Choice 1', 'is_correct': True},
                {'text': 'Choice 2', 'is_correct': False}
            ]
        })
    
    def test_create_question_form_invalid(self):
        with patch('frontend.components.quiz.st') as mock_st:
            mock_st.text_area.return_value = ''
            question = create_question_form(0)
            self.assertIsNone(question)
    
    @patch('frontend.components.quiz.quiz.st')
    def test_handle_image_upload(self, mock_st):
        # Create mock file
        mock_file = MagicMock()
        mock_file.getvalue.return_value = b'test data'
        mock_st.file_uploader.return_value = mock_file
        
        # Mock base64 encoding explicitly
        with patch('base64.b64encode') as mock_b64encode:
            mock_b64encode.return_value = b'encoded_data'
            
            result = handle_image_upload(1)
            
            # Verify the mock calls
            mock_st.file_uploader.assert_called_once_with(
                'Image for question 1', 
                key='q1_image'
            )
            mock_file.getvalue.assert_called_once()
            mock_b64encode.assert_called_once_with(b'test data')
            
            self.assertEqual(result, 'encoded_data')
    
    def test_handle_image_upload_no_file(self):
        with patch('frontend.components.quiz.st') as mock_st:
            mock_st.file_uploader.return_value = None
            result = handle_image_upload(1)
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
