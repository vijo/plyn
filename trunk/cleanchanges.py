#!/usr/bin/python

import re

import cfg
from base import TodoItem, read_and_increment_counter

def clean_todo_file():
	lines_or_items = TodoItem.get_todo_file_as_lines_or_items()

	for i in range(len(lines_or_items)):
		if isinstance(lines_or_items[i], TodoItem):
			if lines_or_items[i].id < 0:
				lines_or_items[i].id = read_and_increment_counter()
	
	TodoItem.save_lines_or_items_array(lines_or_items)


if __name__ == "__main__":
	clean_todo_file()

