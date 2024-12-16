import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_streamlit():
    with patch('frontend.components.auth.st') as mock_st:
        mock_st.session_state = {}
        yield mock_st
