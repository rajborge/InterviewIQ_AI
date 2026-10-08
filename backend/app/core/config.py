from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    app_name:str="InterviewIQ"
    debug:bool=False
    database_url:str

    secret_key:str
    algorithm:str
    access_token_expire_minutes:int

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    gemini_model:str
    gemini_api_key:str

    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings=Settings()