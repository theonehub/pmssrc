from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form

class OAuth2PasswordRequestFormWithHost(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
        client_id: str = Form(None),
        client_secret: str = Form(None),
        hostname: str = Form(...),
    ):
        super().__init__(username=username, password=password, scope=scope, client_id=client_id, client_secret=client_secret)
        self.hostname = hostname
