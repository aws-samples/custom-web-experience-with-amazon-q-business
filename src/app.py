from controllers.streamlit_controller import StreamlitController
from views.user_view import UserView

def main():
    view = UserView()
    StreamlitController(view)

if __name__ == "__main__":
    main()