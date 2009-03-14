import os.path

# Directory where the files are located.
# TODO_FILES_DIR = '/home/username/todofiles'
TODO_FILES_DIR = os.path.join(os.path.dirname(__file__),"..")

TODO_FILE = os.path.join(TODO_FILES_DIR, "todo.txt")
COUNTER_FILE = os.path.join(TODO_FILES_DIR, "count.txt")
LOG_FILE = os.path.join(TODO_FILES_DIR, "log.txt")

BACKUPS_DIR = os.path.join(TODO_FILES_DIR, "backups")

