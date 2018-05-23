#Code writeen by Fredrik Sundström

#All associated files needs to be in the same directory
#By default resuts are written to a csv file in current directory
#For terminal output execute: py user_journeys.py --output=terminal

#To run results for ID: py user_journeys.py --user_id=*your id*

import csv
import numpy as np
import argparse
import sys

FLAGS = None
parser = argparse.ArgumentParser()
parser.add_argument(
	'--user_id',
    type=str,
    default='734c6d42-30f1-47a7-8ceb-e2714302719a',
    help='Random default user id.')

parser.add_argument(
	'--output',
    type=str,
    default='csv',
    help='Output reults to csv by default.')

FLAGS, unparsed = parser.parse_known_args()

RESULT_OUTPUT = FLAGS.output
USER_ID = FLAGS.user_id
FILE_LOGS = 'apache-webserver.logs'
FILE_USER_DATA = 'user_data.csv' 

TARGET_URL_1 = 'https://www.jaguar.co.uk/request-a-brochure/index.html'							#conversion_URL
TARGET_URL_2 = 'https://www.jaguar.co.uk/owners/servicing-maintenance/book-service-online.html'	#conversion_URL
COOKIE_ID = None

def __main__():
	COOKIE_ID = import_user_data(FILE_USER_DATA, FLAGS.user_id) #get cookie ID from user id
	user_logs = import_log_data(FILE_LOGS, COOKIE_ID) #imprt logs by cookie ID
	sorted_user_logs = sort_by_timestamp(user_logs) #sort logs by timestamp: ascending
	user_journeys = find_journeys(sorted_user_logs) 
	print_result(user_journeys)

def import_user_data(filename, user_id):
	
	with open(filename, newline='') as inputfile:
		reader = csv.reader(inputfile, delimiter=',')
		for row in reader:
			row = tuple(row)
			#print(type(row[1]))
			#print(type(user_id))
			if row[1] == user_id:
				COOKIE_ID = row[2]

	return COOKIE_ID

def import_log_data(filename, cookie_id):

	with open(filename, newline='') as inputfile:
		added = set()
		user_found = False
		reader = csv.reader(inputfile, delimiter='|')
		user_logs = list()

		for row in reader:
			row = tuple(row)
			if row[3] == cookie_id:
				if row not in added:
					user_found = True
					user_logs.append(row)
					added.add(row)
		
		if user_found is False:
			print('User with ID "' + FLAGS.user_id + '" does not have any registered journeys')
			sys.exit()
	
	return user_logs	

def sort_by_timestamp(unsorted_user_logs):
	unsorted_user_logs = np.array(unsorted_user_logs)
	sorted_user_logs = unsorted_user_logs[np.argsort(unsorted_user_logs[:,0])]
	
	return sorted_user_logs

def find_journeys(user_logs):
	current_journey = list() #current journey
	all_journeys = list()
	start_time=0 #referrer_1 timestamp
	current_time=0 #page_x timestamp

	for log in user_logs:
		current_time = float(log[0])
		if not current_journey: 
			current_journey.append(log[1])
			current_journey.append(log[2])
			start_time=float(log[0])
		elif (current_time - start_time)/60 < 5: #checks time span between start and current time
			current_journey.append(log[2])
			if log[2] == TARGET_URL_1 or log[2] == TARGET_URL_2: #if conversion url. stop current journey
				all_journeys.append(current_journey)
				current_journey = list()

		else:
			all_journeys.append(current_journey)
			current_journey = list()
			start_time=float(log[0])
			current_journey.append(log[1])
			current_journey.append(log[2])
	
	if current_journey:	
		all_journeys.append(current_journey)

	#print(all_journeys)
	return all_journeys

def print_result(user_journeys):

	if RESULT_OUTPUT == 'terminal':
		print('	All journeys registered to ' + FLAGS.user_id + ' :')
		print('	Total: ' + str(len(user_journeys)))
		print()
		for journey in user_journeys:
			print('Journey: ')
			for page in journey:
				print(str(page) + ' > ', end='')
			print()
			print()
	else:
		print('	Results written to /' + FLAGS.user_id + '_user_journeys.csv')
		with open(FLAGS.user_id + '_user_journeys.csv', 'w') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerows(user_journeys)  

__main__()