from requests import get, codes
import sqlite3
from threading import Thread
from queue import Queue
from os import getenv

# https://stackoverflow.com/questions/40992480/getting-a-soundcloud-api-client-id
CLIENT_ID = getenv("CLIENT_ID", None)

if CLIENT_ID == None:
	print("Set your CLIENT_ID as env variable.")
	exit(1)

API_USERS_BASE_URL = "http://api.soundcloud.com/users/"
CLIENT_ID_PARAMETER = "?client_id=%s" % CLIENT_ID

SCHEMA = """
	create table User (
		id integer primary key,
		username text not null,
		permalink_url text not null,
		track_count integer not null
	);
"""

conn = sqlite3.connect("soundcloud.db", check_same_thread=False)

def db_integrity_check(conn):
	c = conn.cursor()
	c.execute("select sql from sqlite_master where type='table' "
		"and name in ('User')")
	return len(c.fetchall()) == 1


def starting_position(conn):
	c = conn.cursor()
	c.execute("select max(id) from User")
	
	result = c.fetchall()

	if result[0][0] == None:
		return 0
	return result[0][0] + 1

if not db_integrity_check(conn):
	print("Integrity check failed... Recreating database.")
	conn.cursor().executescript(SCHEMA)
	conn.commit()

starting_position_ = starting_position(conn)


# https://www.metachris.com/2016/04/python-threadpool/
class Worker(Thread):
	def __init__(self, tasks):
		super().__init__()
		self.tasks = tasks
		self.daemon = True
		self.start()

	def run(self):
		while True:
			func, args, kargs = self.tasks.get()
			try:
				func(*args, **kargs)
			except Exception as e:
				print(e)
			finally:
				self.tasks.task_done()


class ThreadPool:
	""" Pool of threads consuming tasks from a queue """
	def __init__(self, num_threads):
		self.tasks = Queue(num_threads)
		for _ in range(num_threads):
			Worker(self.tasks)

	def add_task(self, func, *args, **kargs):
		""" Add a task to the queue """
		self.tasks.put((func, args, kargs))


	def wait_completion(self):
		""" Wait for completion of all the tasks in the queue """
		self.tasks.join()


def retrieve_user(conn, request_range):
	c = conn.cursor()

	for user_id in request_range:
		response = get("%s%i%s" % (API_USERS_BASE_URL, user_id, CLIENT_ID_PARAMETER))
		if response.status_code == codes.ok:
			json_response = response.json()
			if json_response["track_count"] > 0:
				c.execute("insert into User (id, username, permalink_url, track_count) values "
					"(?, ?, ?, ?)", (user_id, json_response["username"], 
						json_response["permalink_url"], json_response["track_count"]))
				print("Saved user '%s' (%i)" % (json_response["username"], user_id))
		elif response.status_code == 404:
			print("User '%i' doesn't exist." % user_id)
		else:
			print("\033[31mERROR\033[0m")
			print(response.status_code)
			print(response.text)

	conn.commit()	

print("Starting at user %i" % starting_position_)

# 319479399: last user as of 13 07 2017 22:30

try:
	thread_pool = ThreadPool(5)
	for user_id_range_start in range(starting_position_, 319479399, 10):
		thread_pool.add_task(retrieve_user, conn, range(user_id_range_start, user_id_range_start + 10))
except KeyboardInterrupt:
	print("Stopping...")
	thread_pool.wait_completion()
	print("Stopped.")