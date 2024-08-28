from streamlit_feedback import streamlit_feedback

def handle_feedback():
    """
    Handles feedback from the user after responses are generated.
    """
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional] Please provide an explanation",
    )
    return feedback
