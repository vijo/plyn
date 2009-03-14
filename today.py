#!/usr/bin/python

import copy
import re
from datetime import datetime, timedelta

from base import TodoItemFilteredList

DAYS_COMING_UP = 14

def list_late_and_coming_up(baselist):
	n = copy.deepcopy(baselist)
	n.filter_by_has_datetime_end()
	n.sort_by_datetime_end_reverse()

	if len(n.items) > 0:
		i = 0

		print "\n\n\n"

		if n.items[0].datetime_end < datetime.now():
			print "----- Late tasks ----------------------------------------------"

			while i < len(n.items) and n.items[i].datetime_end < datetime.now():
				print n.items[i]
				i += 1

			print ""

		if i < len(n.items):
			print "----- End date coming up (reverse chronological) --------------"

			while i < len(n.items) and (n.items[i].datetime_end - datetime.now() < timedelta(days=DAYS_COMING_UP)):
				print n.items[i]
				i += 1

			print ""


def list_high_priority(baselist):
	n = copy.deepcopy(baselist)
	n.filter_by_priority(4)

	if len(n.items) > 0:
		print "----- High priority (4-5) -------------------------------------"
		for i in n.items:
			print i

		print ""

def list_waiting_for_feedback(baselist):
	n = copy.deepcopy(baselist)
	n.filter_by_text("+feedback")

	if len(n.items) > 0:
		print "----- Waiting for feedback ------------------------------------"
		for i in n.items:
			print i

		print ""

def todays_items():
	baselist = TodoItemFilteredList()

	list_late_and_coming_up(baselist)
	list_high_priority(baselist)
	list_waiting_for_feedback(baselist)

if __name__ == "__main__":
	todays_items()

