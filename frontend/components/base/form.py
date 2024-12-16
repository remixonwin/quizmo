from typing import Protocol, TypeVar, Generic, Callable, Optional
from dataclasses import dataclass
import streamlit as st

T = TypeVar('T')

class FormData(Protocol):
    """Protocol for form data types"""
    pass

@dataclass
class BaseFormState(Generic[T]):
    """Generic form state container"""
    data: Optional[T] = None
    errors: list[str] = None

class BaseForm(Generic[T]):
    """Enhanced base form with type safety and state management"""
    
    def __init__(self, key: str, submit_label: str):
        self.form_key = key
        self.submit_label = submit_label
        self.state = BaseFormState[T]()

    def render(self, 
              render_content: Callable[[], None],
              handle_submit: Callable[[T], None],
              validate: Optional[Callable[[T], list[str]]] = None) -> None:
        """Generic form renderer with validation"""
        with st.form(key=f"{self.form_key}-form"):
            st.markdown(f'<div data-testid="{self.form_key}-form">', unsafe_allow_html=True)
            render_content()
            
            if st.form_submit_button(self.submit_label):
                if validate:
                    errors = validate(self.state.data)
                    if errors:
                        for error in errors:
                            st.error(error)
                        return
                handle_submit(self.state.data)
            st.markdown('</div>', unsafe_allow_html=True)

class StateManager:
    def __init__(self):
        self.state = {}

    def set(self, key, value):
        self.state[key] = value

    def get(self, key):
        return self.state.get(key)

class FormComponent:
    """Base form component that handles common form functionality"""
    
    def __init__(self, key, title=None):
        """
        Initialize form component.
        Args:
            key (str): Unique form key
            title (str, optional): Form title
        """
        self.key = key
        self.title = title
        self.form = None

    def render(self, render_content_fn, handle_submit_fn):
        """
        Render form with content and submit handler.
        Args:
            render_content_fn: Function to render form contents
            handle_submit_fn: Function to handle form submission
        """
        if self.title:
            st.subheader(self.title)
            
        with st.form(key=self.key, clear_on_submit=True):
            render_content_fn()
            submit_button = st.form_submit_button("Submit")
            
            if submit_button:
                handle_submit_fn()