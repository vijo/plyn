#!/usr/bin/python

# Logs an activity having been done in the past X minutes,
# or just a duration having been done today (no specific time).

import sys
from datetime import datetime, timedelta 

import cfg
from base import TodoItem, datetime_format_pat, date_format_pat

def log_activity(item_id, duration, comments=None):
	item_id = int(item_id)

	only_duration = False
	if duration[0] == '~':
		only_duration = True
		duration = int(duration[1:])
	else:
		duration = int(duration)

	item = TodoItem.get_from_id(item_id)

	if not item.minutes_done:
		item.minutes_done = 0
	item.minutes_done += duration
	item.save()

	ancestor_list = item.get_ancestors_as_list()

	datetime_end = datetime.now()
	datetime_begin = datetime.now() - timedelta(minutes=duration)

	f = open(cfg.LOG_FILE, "a")
	if only_duration:
		f.write("%s	%s|	[%s-]	%d %s\n" %
				("|".join([str(i.id) for i in ancestor_list]),
				"|".join([i.title.strip() for i in ancestor_list]),
				datetime_begin.strftime(date_format_pat),
				duration,
				comments)
			)
	else:
		f.write("%s	%s|	[%s-%s]	%d %s\n" %
				("|".join([str(i.id) for i in ancestor_list]),
				"|".join([i.title.strip() for i in ancestor_list]),
				datetime_begin.strftime(datetime_format_pat),
				datetime_end.strftime(datetime_format_pat),
				duration,
				comments)
			)

	f.close()

args = sys.argv

if len(args) != 3 and len(args) != 4:
	print "Usage: log.py item_id [~]duration_in_minutes comments"
	sys.exit(0)

if len(args) == 3:
	log_activity(args[1], args[2])
else:
	log_activity(args[1], args[2], args[3])


