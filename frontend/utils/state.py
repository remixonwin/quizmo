
from typing import TypeVar, Generic, Optional, Dict, Any
import streamlit as st

T = TypeVar('T')

class StateManager(Generic[T]):
    """Type-safe state management."""
    
    def __init__(self, key: str, default: T):
        self.key = key
        if key not in st.session_state:
            st.session_state[key] = default
            
    @property
    def value(self) -> T:
        return st.session_state[self.key]
        
    @value.setter
    def value(self, new_value: T) -> None:
        st.session_state[self.key] = new_value