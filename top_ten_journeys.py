#Code writeen by Fredrik Sundström

#All associated files needs to be in the same folder

#By default resuts are written to a csv file in current directory
#For terminal output execute: py top_ten_journeys.py --output=terminal

import csv
import numpy as np
import operator as op
import argparse

FLAGS = None
parser = argparse.ArgumentParser()
parser.add_argument(
	'--output',
    type=str,
    default='csv',
    help='Output reults to csv by default.')

FLAGS, unparsed = parser.parse_known_args()

RESULT_OUTPUT = FLAGS.output
FILE_LOGS = 'apache-webserver.logs'

TARGET_URL_1 = 'https://www.jaguar.co.uk/request-a-brochure/index.html'							#conversion_URL
TARGET_URL_2 = 'https://www.jaguar.co.uk/owners/servicing-maintenance/book-service-online.html'	#conversion_URL

#Main function
def __main__():
	data, cookie_ids = import_log_data(FILE_LOGS) #import logdata from file 'apache-webserver.logs'
	processed_dataset = remove_non_relevant_data(data, cookie_ids) #removes any unvanted records
	unsorted_id_batches = sort_by_cookie_ID(processed_dataset) #sort records by cookie_ID
	sorted_id_batches = sort_by_timestamp(unsorted_id_batches) #store batches by ascending timestamp
	top_10_journeys = find_journey(sorted_id_batches)
	results_to_file(top_10_journeys) #Writes result to file alternativly to terminal

#imports records and ignore duplicates
def import_log_data(filename):
	added = set() #tracks added records
	relevant_cookie_ids = set() #stores id_tags with conversion urls
	
	if filename.endswith('.csv'):
		delimiter=','
	else:
		delimiter='|'

	with open(filename, newline='') as inputfile:
		reader = csv.reader(inputfile, delimiter=delimiter)
		data = list()
		for row in reader:
			row = tuple(row) #list not hashable
			if row not in added: 
				added.add(row)
				data.append(row)
				if str(row[2]) == TARGET_URL_1 or str(row[2]) == TARGET_URL_2: #store id if record is conversion url
					relevant_cookie_ids.add(row[3])
			
	return data,relevant_cookie_ids

#removes any records non referring to cookie ids with conversion urls
def remove_non_relevant_data(data, relevant_cookie_ids):
	new_data = list()
	
	for row in data:
		if row[3] in relevant_cookie_ids:
			new_data.append(row)

	return new_data

#split data by cookie ids
def sort_by_cookie_ID(data):
	unsorted_id_batches = list() 
	current_batch = list()
	data = np.array(data)	
	data = data[np.argsort(data[:,3])] #sort/groups database by cookie_id7
	current_ID = data[0][3] 
	previous_ID = data[0][3]
	biggest_batch = [0]*2

	for row in data:
		current_ID = row[3]
		if current_ID == previous_ID:
			current_batch.append(row)	
		else:
			unsorted_id_batches.append(current_batch) #add batch to list
			if len(current_batch) > biggest_batch[0]:
				biggest_batch[0] = len(current_batch)
				biggest_batch[1] = current_ID
			
			current_batch = list() #empty list
			current_batch.append(row)
			previous_ID=current_ID 

	return unsorted_id_batches

#sort barches by timestamp Note: flawed. Works since all timestamp values starts with 1 is equal length. #argsort(unsorted_batch[:,0])] sort by string
def sort_by_timestamp(unsorted_id_batches):
	sorted_id_batches = list()

	for unsorted_batch in unsorted_id_batches:
		unsorted_batch = np.array(unsorted_batch)
		batch_sorted = unsorted_batch[np.argsort(unsorted_batch[:,0])]
		sorted_id_batches.append(batch_sorted)

	return sorted_id_batches

#Iterates through each sorted batch and maps journey.
def find_journey(sorted_id_batches):
	journey = list() #current journey
	journey_count = dict() #store journey and frequency
	start_time=None #referrer_1 timestamp
	current_time=None #page_x timestamp
	top_ten_journeys = [('initial',0)]*10 #stores top 10 frequent results

	for batch in sorted_id_batches:
		target =False
		for i in range(0,len(batch)):
			start_time = batch[i][0]
			journey=list()
			if target == False:
				for y in range(i,len(batch)):
					current_time=batch[y][0]
					if (float(current_time) - float(start_time))/60>5:
						break
					elif (batch[y][2] == TARGET_URL_1 or batch[y][2] == TARGET_URL_2):
						target=True
						if not journey: 
							journey.append(batch[y][1])
							journey.append(batch[y][2])
						else:
							journey.append(batch[y][2])
						if str(journey) in journey_count:
							journey_count.update({str(journey):journey_count.get(str(journey)) + 1})		
						else:
							journey_count.update({str(journey):1})
						break
					else:
						if not journey: 
							journey.append(batch[y][1])
							journey.append(batch[y][2])
						else:
							journey.append(batch[y][2])	
			else:
				break

	journeys_results = journey_count.items()

	#Save top 10 frequent journeys in new list
	totCon = 0
	for key, value in journeys_results:
		totCon = totCon + value
		top_ten_journeys.sort(key=op.itemgetter(1))
		new_pair= (key,value)
		if value > top_ten_journeys[0][1]:
			top_ten_journeys[0] = new_pair

	print(totCon)
	return top_ten_journeys

def results_to_file(top_ten_journeys):

	if RESULT_OUTPUT == 'terminal':
		print('----Top 10 most common journeys that end with a conversion----')
		print('Legend: (journey, frequency]')
		i = 9
		
		while i >= 0:
			print()
			print(top_ten_journeys[i])
			i -= 1
	else:
		print('Results written to /top_ten.csv')
		columns_names = ['journey','Frequency']
		
		with open('top_ten.csv', 'w') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerow(columns_names)
			writer = csv.writer(f, delimiter=',')
			writer.writerows(top_ten_journeys) 

__main__()
