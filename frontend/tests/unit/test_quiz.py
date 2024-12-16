import unittest
from frontend.components.quiz import create_question_form, handle_image_upload
from unittest.mock import patch

class TestQuizComponents(unittest.TestCase):
    
    @patch('frontend.components.quiz.st')
    def test_create_question_form_valid(self, mock_st):
        mock_st.text_area.return_value = 'Sample Question'
        mock_st.number_input.return_value = 4
        mock_st.text_input.side_effect = ['Choice 1', 'Choice 2', 'Choice 3', 'Choice 4']
        
        question = create_question_form(0)
        self.assertIsNotNone(question)
        self.assertEqual(question['text'], 'Sample Question')
        self.assertEqual(len(question['choices']), 4)
    
    @patch('frontend.components.quiz.st')
    def test_create_question_form_invalid(self, mock_st):
        mock_st.text_area.return_value = ''
        question = create_question_form(0)
        self.assertIsNone(question)
    
    @patch('frontend.components.quiz.base64')
    @patch('frontend.components.quiz.st.file_uploader')
    def test_handle_image_upload(self, mock_file_uploader, mock_base64):
        mock_file = unittest.mock.Mock()
        mock_file.getvalue.return_value = b'binarydata'
        mock_file_uploader.return_value = mock_file
        mock_base64.b64encode.return_value = b'encodeddata'
        
        result = handle_image_upload(1)
        self.assertEqual(result, 'encodeddata')
    
    @patch('frontend.components.quiz.st.file_uploader')
    def test_handle_image_upload_no_file(self, mock_file_uploader):
        mock_file_uploader.return_value = None
        result = handle_image_upload(1)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
