class AppError(Exception):
    """Base class for application-level errors that routes know how to translate."""

class EmailAlreadyExistsError(AppError):
    def __init__(self,email:str):
        self.email=email
        super().__init__(f"Email Already Registered :{email}")

class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__("Invalid email or password")

class OAuthOnlyAccountError(AppError):
    def __init__(self):
        super().__init__("This account uses Google sign-in.Please log in with Google.")

class InvalidRefreshTokenError(AppError):
    def __init__(self):
        super().__init__("Refresh token is invalid,expired or revoked")

class InvalidFileTypeError(AppError):
    def __init__(self):
        super().__init__("Only PDF files are supported")

class FileTooLargeError(AppError):
    def __init__(self, max_mb: int):
        super().__init__(f"File exceeds the maximum size of {max_mb}MB")