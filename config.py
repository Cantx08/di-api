import os
from dotenv import load_dotenv

load_dotenv()

SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")
SJR_CSV_PATH = os.getenv("SJR_CSV_PATH")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
SJR_BLOB_NAME = os.getenv("SJR_BLOB_NAME")
AREAS_BLOB_NAME = os.getenv("AREAS_BLOB_NAME")