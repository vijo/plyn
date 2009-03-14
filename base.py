#!/usr/bin/python

import os.path
import re
import copy
from datetime import datetime, timedelta, date

import cfg

##############################################################################
# Patterns for parsing the todo.txt file

# Empty lines and comment lines
noop_line_re = re.compile(r"(\s*$|\s*--)")

todo_line_re = re.compile(r"""(?P<indent>\t*)
				(?P<id>\#|\d+)
				\s+
				(?P<title>[^\[<>\|\{\}]+)
				(\s|$)				# trick to remove last space from title
				(\|+
					(\{(?P<priority>[12345])\})?

					\s?

					(\<
						(?P<minutes_done>\d*)
					\/
						(?P<minutes_to_do>\d*)
					\>)?

					\s?

					(\[
						(
							(?P<datetime_begin>(\d\d\d\d\/)?\d\d\/\d\d(\s\d\d:\d\d)?)
							|
							(\+(?P<datetime_begin_plus>\d+))
						)?
						\s*-\s*
						(
							(?P<datetime_end>(\d\d\d\d\/)?\d\d\/\d\d(\s\d\d:\d\d)?)
							|
							(\+(?P<datetime_end_plus>\d+))
						)?
					\])?

					\s*

					(?P<comments>.*)
				)?
				""", re.X)


##############################################################################
# Main class used to represent a todo.txt line

class TodoItem:
	def __init__(self):
		self.indent = None

		self.parent_id = None
		self.parent_obj = None

		self.id = None		# int, < 0 if not set
		self.title = None
		self.priority = None

		self.minutes_done = None
		self.minutes_to_do = None

		self.datetime_begin = None
		self.datetime_end = None

		self.comments = None

	# Customized so the dates are copied, not pointer-assigned
	def __copy__(self):
		newitem = TodoItem()

		newitem.indent = self.indent

		newitem.parent_id = self.parent_id
		newitem.parent_obj = self.parent_obj # only pointer

		newitem.id = self.id
		newitem.title = self.title
		newitem.priority = self.priority

		newitem.minutes_done = self.minutes_done
		newitem.minutes_to_do = self.minutes_to_do

		newitem.datetime_begin = copy.copy(self.datetime_begin)
		newitem.datetime_end = copy.copy(self.datetime_end)

		newitem.comments = self.comments

		return newitem

	def init_from_todotxt_line(self, line, parent_stack):
		m = todo_line_re.match(line)

		if not m:
			print "No match"
		else:
			self._init_with_todotxt_line_match(m, parent_stack)

	# Grabs the match groups and configures the TodoItem properly
	# The hierarchy is reconstructed through the parent_stack parameter,
	# which is the list of parents (objects) of the previously processed item.
	def _init_with_todotxt_line_match(self, match, parent_stack):
		#######################
		# Basic/required info

		if match.group('indent'):
			self.indent = len(match.group('indent'))
		else:
			self.indent = 0

		if match.group('id') == "#":
			self.id = -1
		else:
			self.id = int(match.group('id'))

		# Find the right parent object and change the parent_stack
		# to reflect the current item's ancestor list
		if self.indent > 0:
			self.parent_id = parent_stack[self.indent-1].id
			parent_stack[self.indent:] = [self]
		else:
			self.parent_id = None
			parent_stack[0:] = [self]

		self.title = match.group('title').strip()

		#######################
		# Priority

		if match.group('priority'):
			self.priority = int(match.group('priority'))

		#######################
		# Time done/expected

		if match.group('minutes_done'):
			self.minutes_done = int(match.group('minutes_done'))
		if match.group('minutes_to_do'):
			self.minutes_to_do = int(match.group('minutes_to_do'))

		#######################
		# Datetimes

		today = date.today()
		today = datetime(today.year, today.month, today.day)

		if match.group('datetime_begin'):
			self.datetime_begin = parse_incomplete_datetime(match.group('datetime_begin'))
		elif match.group('datetime_begin_plus'):
			self.datetime_begin = today + timedelta(days=int(match.group('datetime_begin_plus')))

		if match.group('datetime_end'):
			self.datetime_end = parse_incomplete_datetime(match.group('datetime_end'))
		elif match.group('datetime_end_plus'):
			self.datetime_end = today + timedelta(days=int(match.group('datetime_end_plus')))

		#######################
		# Comments

		if match.group('comments'):
			self.comments = match.group('comments')

	# Returns a string representation suitable to be outputed in the todo.txt file
	def __str__(self):
		ret = []

		ret.append(self.indent * "\t" + str(self.id))

		ret.append(self.title)

		if self.priority != None \
			or self.minutes_done != None or self.minutes_to_do != None \
			or self.datetime_begin != None or self.datetime_end != None \
			or self.comments != None:
			ret.append('|||')

		if not self.priority is None:
			ret.append("{%d}" % self.priority)

		if (not self.minutes_done is None) or (not self.minutes_to_do is None):
			ret2 = []
			ret2.append("<")
			if not self.minutes_done is None:
				ret2.append(str(self.minutes_done))
			ret2.append("/")
			if not self.minutes_to_do is None:
				ret2.append(str(self.minutes_to_do))
			ret2.append(">")
			ret.append(''.join(ret2))

		if (not self.datetime_begin is None) or (not self.datetime_end is None):
			ret2 = []
			ret2.append("[")
			if not self.datetime_begin is None:
				ret2.append(format_datetime(self.datetime_begin))
			ret2.append("-")	
			if not self.datetime_end is None:
				ret2.append(format_datetime(self.datetime_end))
			ret2.append("]")
			ret.append(''.join(ret2))

		if not self.comments is None:
			ret.append(self.comments)

		return " ".join(ret)

	@staticmethod
	def get_from_id(id, all_items=None):
		if not all_items:
			all_items = TodoItem.get_all_todo_items()

		for o in all_items:
			if o.id == id:
				return o

		raise Exception

	# Recursively grabs ancestors of the Item and gives it as a list,
	# starting with top-level, ending with the node itself
	def get_ancestors_as_list(self):
		if self.parent_obj:
			return parent_obj.get_ancestors_as_list() + [self]
		return [self]

	# WARNING: this overwrites the current file, and rereads if if needed.
	# Only to be used for operations targetting a specific item (like changing its priority etc.).
	def save(self, lines_or_items=None):
		if not lines_or_items:
			lines_or_items = TodoItem.get_todo_file_as_lines_or_items()

		for i in range(len(lines_or_items)):
			if isinstance(lines_or_items[i], TodoItem) and lines_or_items[i].id == self.id:
				lines_or_items[i] = self

		TodoItem.save_lines_or_items_array(lines_or_items)

	@staticmethod
	def get_all_todo_items():
		lines_or_items = TodoItem.get_todo_file_as_lines_or_items()
		# Filter to only have items, not lines
		return [i for i in lines_or_items if isinstance(i, TodoItem)]

	@staticmethod
	def get_todo_file_as_lines_or_items():
		f = open(cfg.TODO_FILE, "r")

		lines_or_items = []
		parent_stack = []

		for line in f:
			if noop_line_re.match(line):
				lines_or_items.append(line.rstrip('\n\r'))
				continue

			line = line.rstrip('\n\r')

			t = TodoItem()
			t.init_from_todotxt_line(line, parent_stack)

			if t.id < 0:
				t.id = read_and_increment_counter()

			lines_or_items.append(t)

		f.close()

		return lines_or_items

	@staticmethod
	def save_lines_or_items_array(lines_or_items):
		f = open(cfg.TODO_FILE, "w")
		f.write("\n".join([str(o) for o in lines_or_items]))
		f.close()

##############################################################################
# Todo items container class with filtering methods

class TodoItemFilteredList:
	def __init__(self):
		self.items = TodoItem.get_all_todo_items()

	def filter_by_text(self, text):
		newitems = []
		for i in self.items:
			if text in i.title or (i.comments and text in i.comments):
				newitems.append(i)

		self.items = newitems

	def filter_by_priority(self, minPriority):
		newitems = []
		for i in self.items:
			if i.priority and i.priority >= minPriority:
				newitems.append(i)

		self.items = newitems

	def filter_by_has_datetime_end(self):
		self.items = [i for i in self.items if i.datetime_end]

	def sort_by_datetime_end_reverse(self):
		def date_compare(x, y):
			if x.datetime_end > y.datetime_end:
				return 1
			elif x.datetime_end == y.datetime_end:
				return 0
			else: # x<y
				return -1

		self.items.sort(date_compare)

##############################################################################
# Date handling

incomplete_date_re = re.compile(r"""
				(
					(?P<year>\d\d\d\d)
				\/)?
				(?P<month>\d\d)
				\/
				(?P<day>\d\d)
				(\s
					(?P<hour>\d\d)
					\:
					(?P<minutes>\d\d)
				)?
				""", re.X)

date_format_pat = "%Y/%m/%d"
datetime_format_pat = "%Y/%m/%d %H:%M"

def format_datetime(dt):
	if dt.minute == 0 and dt.second == 0:
		return dt.strftime(date_format_pat)
	else:
		return dt.strftime(datetime_format_pat)

def parse_incomplete_datetime(datetime_str):
	m = incomplete_date_re.match(datetime_str)

	if not m:
		raise Exception

	year = datetime.now().year
	if m.group('year'):
		year = int(m.group('year'))

	hour = minutes = 0
	if m.group('hour'):
		hour = int(m.group('hour'))
		minutes = int(m.group('minutes'))

	return datetime(year,
			int(m.group('month')),
			int(m.group('day')),
			hour,
			minutes)


##############################################################################
# Generic utils

def read_and_increment_counter():
	c = 1

	if os.path.exists(cfg.COUNTER_FILE):
		f = open(cfg.COUNTER_FILE, "r")
		c = f.readline()
		c = int(c)
		f.close()
	
	c += 1

	f = open(cfg.COUNTER_FILE, "w")
	f.write(str(c))
	f.close()

	return c-1



