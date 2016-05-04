from pprint import pprint
import requests as re
from requests.auth import HTTPBasicAuth
import json
import time
from datetime import datetime
from copy import copy
import ast


UNIX_EPOCH_TIME_UTC=0

DIRECTORY='/home/preston/Desktop/Programming/datasci/projects/blog_finder/data/stackexchange/'

ACCESS_TOKEN=''
HEADER2={'':''}

ID=7051
SECRET='##############'
REDIRECT_URI='tphinkle.github.io'
STATE='CALIFORNIA'
SCOPE='no_expiry'

KEY='twKn0n5t7XlbNJSC*77zig(('

LAST_REQUEST_TIME=0

REQUEST_PERIOD=1./30

#def authenticate():
	#global ACCESS_TOKEN
    #global HEADER2
    #client_auth=HTTPBasicAuth(ID, SECRET)
    #auth_request=requests.post("https://stackexchange.com/oauth/dialo",\
    #auth=client_auth, data=POST_DATA, headers=HEADER1)
        #
    #AUTHENTICATION_TIME=datetime.utcnow()
    #ACCESS_TOKEN=auth_request.json()['access_token']
    #HEADER2={"Authorization": "bearer "+str(ACCESS_TOKEN), "User-Agent": "BlogFinder by /u/tphinkle"}
        
    #return

def submit_query(query):
	global LAST_REQUEST_TIME
	if time.time()-LAST_REQUEST_TIME < REQUEST_PERIOD:
		time.sleep(time()-LAST_REQUEST_TIME)
	LAST_REQUEST_TIME=time.time()
	answer=re.get(query).json()
	return answer

def get_questions(community, t1, t2):
	questions=submit_query('https://api.stackexchange.com/2.2/questions?fromdate='+t1+'&todate='+t2+'&order=asc&min=100&sort=creation&site='+community+'&filter=withbody&key='+KEY)
	return questions

def get_question_ids(questions):
	question_ids=[]
	for i in len(questions['items']):
		question_ids.append(questions['items'][i]['question_id'])
	return question_ids

def save_questions(community, questions):
	output_filehandle=open(DIRECTORY+community+'_questions', 'a')
	print questions['items'][-1]['creation_date']
	json.dump(questions, output_filehandle)
	output_filehandle.write('\n')
	output_filehandle.close()
	return

def get_answers(community, t1, t2):
	answers=submit_query('https://api.stackexchange.com/2.2/comments?fromdate='+t1+'&todate='+t2+'&order=asc&min=100&sort=creation&site='+community+'&filter=withbody&key='+KEY)
	try:
		print answers['items'][-1]['creation_date']
	except:
		print answers
	return answers

def save_answers(community, answers):
	output_filehandle=open(DIRECTORY+community+'_answers', 'a')
	
	print answers['items'][-1]['creation_date']
	
	json.dump(answers, output_filehandle)
	output_filehandle.write('\n')
	output_filehandle.close()
	
	return


def get_all_questions(community):
	keep_going=True

	questions_filename=DIRECTORY+community+'_questions'


	try:
		questions_filehandle=open(questions_filename, 'r')
		line=' '
		while line:
			line=questions_filehandle.readline()
		t1=str(int(json.loads(line)['items']['created_utc']))
		questions_filehandle.close()
	except: 
		t1='0'
	t2=str(int(time.time()))
	t1='0'
	while keep_going == True:

		questions=get_questions(community, t1, t2)
		save_questions(community, questions)

		#answers=get_answers(community, t1, t2)
		#save_questions

		#question_ids=get_question_ids(questions)
		#for question_id in question_ids:
			#answers=get_answers(community, question_ids)
			#save_answers(community, answers)

		if (questions['quota_remaining'] <= 0) | (questions == None):
			keep_going=False

		if keep_going==True:
			t1=str(int(questions['items'][-1]['creation_date']+1))
			t2=str(int(time.time()))



	return questions


def get_all_answers(community):
	keep_going=True

	answers_filename=DIRECTORY+community+'_questions'


	try:
		answers_filehandle=open(answers_filename, 'r')
		line=' '
		while line:
			line=answers_filehandle.readline()
		t1=str(int(json.loads(line)['items'][-1]['created_utc']))
		answers_filehandle.close()
	except: 
		t1='0'
	t2=str(int(time.time()))
	t1='1223910467'
	while keep_going == True:

		answers=get_answers(community, t1, t2)

		save_answers(community, answers)



		if (answers['quota_remaining'] <= 0) | (answers == None):
			keep_going=False

		if keep_going==True:
			t1=str(int(answers['items'][-1]['creation_date']+1))
			t2=str(int(time.time()))



	return answers



	

