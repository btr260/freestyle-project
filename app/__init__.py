import os
from dotenv import load_dotenv

load_dotenv()

# use "production" on a remote server
APP_ENV = os.getenv("APP_ENV", default="development")
