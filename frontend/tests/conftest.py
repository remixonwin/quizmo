import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_streamlit():
    with patch('streamlit.runtime.scriptrunner.ScriptRunContext') as mock_ctx:
        mock_ctx.get_script_run_ctx = MagicMock()
        # Removed the global patching of 'frontend.components.quiz.st'
        # This allows individual tests to patch 'st' as needed
        yield
