import os

DEFAULT_RECORDS_COUNT = 1000
DEFAULT_FILE_NAME = "user_drugs.json"
DEFAULT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), f"generated/{DEFAULT_FILE_NAME}"
)
MIN_USER_DRUGS = 2
MAX_USER_DRUGS = 5

WEEKDAYS = [
    "SUNDAY",
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
]
