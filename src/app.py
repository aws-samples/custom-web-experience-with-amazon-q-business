from streamlit_controller import StreamlitController
from user_view import UserView

def main():
    view = UserView()
    StreamlitController(view)

if __name__ == "__main__":
    main()