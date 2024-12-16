import streamlit as st

class FormComponent:
    def __init__(self, form_key, submit_label):
        self.form_key = form_key
        self.submit_label = submit_label

    def render(self, render_content_func, handle_submit_func):
        # Add container div for form styling and testing
        st.markdown(f'<div data-testid="{self.form_key}-form">', unsafe_allow_html=True)
        
        # Create the form
        with st.form(key=f"{self.form_key}-form"):
            # Create container for form fields
            st.markdown('<div class="form-fields">', unsafe_allow_html=True)
            
            # Call content function that defines the fields
            render_content_func()
            
            # Close form fields container
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add submit button
            if st.form_submit_button(self.submit_label):
                handle_submit_func()
                
        st.markdown('</div>', unsafe_allow_html=True)