# from flask_login import UserMixin
from quart_auth import AuthUser
from typing import Union

# AuthUser()

class User(AuthUser):
    def __init__(self, auth_id:Union[int, str], username:str, email:str):
        super().__init__(auth_id)
        self.email = email
        self.username = username
    
    # def __init__(self, auth_id:Union[int, str],username:str, email:str) -> None:

        
    #     self.auth_id = auth_id
    #     self.username = username
    #     self.email = email
