import unittest
from frontend.components.base.form import BaseForm, StateManager
from unittest.mock import patch

class TestBaseForm(unittest.TestCase):
    
    @patch('frontend.components.base.form.st')
    def test_base_form_render(self, mock_st):
        def mock_render_content():
            mock_st.write("Form Content")
        
        def mock_handle_submit(data):
            pass
        
        form = BaseForm(key="test_form", submit_label="Submit")
        form.render(mock_render_content, mock_handle_submit)
        mock_st.write.assert_called_with("Form Content")
    
    def test_state_manager_get_set(self):
        with patch('frontend.components.base.form.st.session_state', {}) as mock_session:
            state = StateManager()
            state.set("test_key", "test_value")
            assert state.get("test_key") == "test_value"

if __name__ == '__main__':
    unittest.main()
