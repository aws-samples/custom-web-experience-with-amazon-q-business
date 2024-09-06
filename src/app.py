from controllers.init_config_controller import InitConfigController
from controllers.auth_controller import AuthController
from controllers.chat_controller import ChatController
from views.auth_view import AuthView
from views.user_view import UserView

def main():
    InitConfigController()
    
    auth_view = AuthView()
    auth_controler = AuthController(auth_view)
    is_authenticated = auth_controler.authenticate()
    
    if is_authenticated:
        user_view = UserView()
        ChatController(user_view)

if __name__ == "__main__":
    main()