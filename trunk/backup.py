#!/usr/bin/python

# Make a copy of the todo.txt file, in case something goes wrong.

import os.path
import shutil
from datetime import datetime

import cfg

def dobackup():
	src_file = cfg.TODO_FILE

	datestamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")

	dest_file = os.path.join(cfg.BACKUPS_DIR, "todo_" + datestamp + ".txt")

	shutil.copy(src_file, dest_file)

if __name__ == "__main__":
	dobackup()


