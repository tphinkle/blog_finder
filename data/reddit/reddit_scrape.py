from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from datetime import datetime
from copy import copy
import ast


MAX_ADDITIONAL_COMMENTS=20


AUTHENTICATION_TIME=time.time()
AUTHENTICATION_DURATION=60*60
AUTHENTICATION_EPSILON=10
LAST_REQUEST_TIME_MS=0
REQUEST_EPSILON_MS=2000.
SUBMISSION_TIME_DELTA=96*60*60

ACCESS_TOKEN=''
ID='nEDSIP0HAp61JA'
SECRET='###########'
USERNAME='tphinkle'
PASSWORD='###########'

REDDIT_FIRST_EPOCH=1119581033


POST_DATA={"grant_type": "password", "username": "tphinkle", "password": "#########"}
HEADER1={"User-Agent": "BlogFinder by /u/tphinkle"}
HEADER2={}

RAW_OUTPUT_DIRECTORY='/home/preston/Desktop/Programming/datasci/projects/blog_finder/'\
'data/reddit/'


def current_time_MS():
    return int(round(time.time()*1000.))

def check_valid_token():
    valid_token=True
    if time.time()-AUTHENTICATION_TIME>AUTHENTICATION_DURATION-AUTHENTICATION_EPSILON:
        valid_token=False
    return valid_token

def authenticate():
    global ACCESS_TOKEN
    global HEADER2
    if (check_valid_token() == False) | (ACCESS_TOKEN==''):
        client_auth=HTTPBasicAuth(ID, SECRET)
        auth_request=requests.post("https://www.reddit.com/api/v1/access_token",\
            auth=client_auth, data=POST_DATA, headers=HEADER1)
        
        AUTHENTICATION_TIME=datetime.utcnow()
        ACCESS_TOKEN=auth_request.json()['access_token']
        HEADER2={"Authorization": "bearer "+str(ACCESS_TOKEN), "User-Agent": "BlogFinder by /u/tphinkle"}
        
    return

def make_request(string):
    global LAST_REQUEST_TIME_MS
    sleep_time=(1.*REQUEST_EPSILON_MS-(current_time_MS()-LAST_REQUEST_TIME_MS))/1000.0
    if sleep_time > 0:
        time.sleep(sleep_time)  

    response = requests.get(string, headers=HEADER2).json()
    LAST_REQUEST_TIME_MS=current_time_MS()

    return response

def get_submissions(subreddit, t1, t2):
    submissions=[]
    search_string=r'https://reddit.com/r/'+subreddit+'/search.json?q=timestamp:'+str(t1)+'..'+str(t2)+\
    '&sort=new&restrict_sr=on&syntax=cloudsearch'
    submissions=make_request(search_string)
    return submissions

def save_submission(submission, raw_output_filehandle):
    json.dump(submission['data'], raw_output_filehandle)
    raw_output_filehandle.write('\n\n')

    return

def get_all_comments(submission, raw_output_filehandle):
    search_string=r'https://reddit.com/comments/'+submission['data']['id']+'.json'
    all_comments=make_request(search_string)
    parent=all_comments[-1]['data']
    get_comments(parent, all_comments[0]['data']['children'][0]['data']['name'], raw_output_filehandle)
    return

def get_comments(parent, link_id, raw_output_filehandle):
    additional_comment_ids=[]
    for i in range(len(parent['children'])):
        try:
            save_comment(parent['children'][i]['data'], raw_output_filehandle)
            new_parent=parent['children'][i]['data']['replies']['data']
            get_comments(new_parent, link_id)
        except:
            if parent['children'][i]['kind']=='more':
                for child_id in parent['children'][i]['data']['children']:
                    additional_comment_ids.append(child_id)

    while len(additional_comment_ids)>0:
        additional_comment_ids_string=''
        if len(additional_comment_ids)>MAX_ADDITIONAL_COMMENTS:
            length=MAX_ADDITIONAL_COMMENTS
        else:
            length=len(additional_comment_ids)
        for i in range(length):
            if i == length-1:
                additional_comment_ids_string+=additional_comment_ids[i]
            else:
                additional_comment_ids_string+=additional_comment_ids[i]+','
        additional_comment_ids=additional_comment_ids[length:]

        additional_comments=make_request('https://oauth.reddit.com/api/morechildren.json?api_type=json&link_id='+link_id+\
            '&children='+additional_comment_ids_string)

        save_additional_comments(additional_comments,raw_output_filehandle)

    return


def save_comment(comment, raw_output_filehandle):
    temp_comment=copy(comment)
    del temp_comment['replies']
    
    json.dump(temp_comment, raw_output_filehandle)
    raw_output_filehandle.write('\n\n')
    #raw_output_filehandle.write(str(temp_comment))
    #raw_output_filehandle.write('\n\n')
    return

def save_additional_comments(additional_comments, raw_output_filehandle):
    for thing in additional_comments['json']['data']['things']:
        json.dump(thing['data'], raw_output_filehandle)
        raw_output_filehandle.write('\n\n')
    return

def get_last_time(raw_output_filehandle):
    file_contents=raw_output_filehandle.read()
    if file_contents != '':
        last_entry=file_contents.split('\n')[-2].replace('\'','\\"')
        last_entry_json=json.loads(last_entry)
        last_time=int(last_entry_json['created_utc'])
    else:
        last_time = REDDIT_FIRST_EPOCH

    print last_time
    return last_time

def get_subreddit(subreddit,t1=-1,t2=-1):
    keep_going=True
    raw_output_filehandle=open(RAW_OUTPUT_DIRECTORY+subreddit, 'a+')
    if t1 == -1:
        t1=get_last_time(raw_output_filehandle)
        t2=t1+SUBMISSION_TIME_DELTA
    while keep_going==True:
        print 'getting subreddit... t1=',t1,'\tt2=',t2
        authenticate()
        submissions=get_submissions(subreddit, t1, t2)
        num_submissions=len(submissions['data']['children'])
        print 'num_submissions = ', num_submissions

        for submission in submissions['data']['children']:
            save_submission(submission, raw_output_filehandle)
            get_all_comments(submission, raw_output_filehandle)

        if (num_submissions==0):
            t1=int(t2)
        elif int(submissions['data']['children'][0]['data']['created_utc'])==t1:
            t1=int(t2)
        else:
            t1=int(submissions['data']['children'][0]['data']['created_utc'])
        t2=int(t1+SUBMISSION_TIME_DELTA)

        if t2>time.time():
            keep_going=False

    return

