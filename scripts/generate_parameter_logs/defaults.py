import os

DEFAULT_RECORDS_COUNT = 500_000
DEFAULT_FILE_NAME = "parameter_logs.json"
DEFAULT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), f"generated/{DEFAULT_FILE_NAME}"
)
