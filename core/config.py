from pydantic_settings import BaseSettings, SettingsConfigDict

# অ্যাপ্লিকেশন সেটিং কনফিগারেশন ক্লাস
# এটি .env ফাইল থেকে এনভায়রনমেন্ট ভেরিয়েবলগুলো পড়ে নেবে
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore", # অতিরিক্ত কোনো ভেরিয়েবল থাকলে সেটি ইগনোর করবে
    )
    # নিচে দেওয়া ভেরিয়েবলগুলো .env ফাইলে থাকতে হবে
    DB_CONNECTION: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    SENDER_EMAIL: str
    SENDER_EMAIL_PASSWORD: str

# সেটিংস অবজেক্ট তৈরি করা হলো যা পুরো প্রোজেক্টে ব্যবহার করা হবে
settings = Settings()