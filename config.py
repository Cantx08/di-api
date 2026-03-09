import os
from dotenv import load_dotenv

load_dotenv()

SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")
SJR_CSV_PATH = os.getenv("SJR_CSV_PATH")