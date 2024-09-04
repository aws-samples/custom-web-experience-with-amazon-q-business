from controllers.init_config_controller import InitConfigController
from controllers.auth_controller import AuthController
from controllers.chat_controller import ChatController
from views.user_view import UserView

def main():
    view = UserView()
    InitConfigController()
    AuthController(view)
    ChatController(view)

if __name__ == "__main__":
    main()