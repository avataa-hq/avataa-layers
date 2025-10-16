import os

DEBUG = os.environ.get(
    "DEBUG", "False"
).upper() in ("TRUE", "Y", "YES", "1")
