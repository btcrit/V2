"""
fourchain - a mix of 4chan, blockchain, and fortune
Scan 4chan's /biz/ board for cryptocurrency ticker symbols.
"""

from time import sleep
import re
from string import punctuation
import operator
import requests


def getindexjson():
    "Get the /biz/ index json"
    print("Getting index data...")
    indexjson = requests.get('http://a.4cdn.org/biz/threads.json').json()
    print("Index data retrieved.")
    return indexjson

def getnums(indexjson):
    "get thread numbers from index data"
    nums = []
    print("Processing index...")
    for page in indexjson:
        for thread in page['threads']:
            nums.append(thread['no'])
    print("Retrieved "+str(len(nums))+" thread references.")
    return nums


def getthread(num):
    "Get a thread given its ID"
    print("Retrieving thread "+str(num)+"...")
    thread = requests.get(
        'http://a.4cdn.org/biz/thread/'+str(num)+'.json'
    ).json()
    print("Thread Retrieved")
    return thread

def printthread(thread):
    "prints a thread"
    if 'sub' in thread['posts'][0]:
        sub = thread['posts'][0]['sub']
        print("subject: \'"+str(sub)+"\'")
    else:
        print("No subject")
    for post in thread['posts']:
        print("")
        if 'com' in post:
            comment = post['com']
            print(processcomment(comment))
        elif 'filename' in post:
            print("Image only post: "+str(post['filename']))
        else:
            print("Post with no comment and no associated file?")
            print(post)

def processcomment(com):
    "process a comment to remove html, etc."
    # remove &#039; (apostrophe) and others
    #com = re.sub(r"&#\d{3};", "", com)
    # remove br tags
    com = re.sub("</?br>", " ", com)
    # remove the link tags around reply links
    com = re.sub("</?a.*\"?>", "", com)
    # remove span class=quote
    com = re.sub("</?span.*>", "", com)
    # remove greater than, less than chars
    #com = re.sub("&..;", "", com)
    # remove html escaped chars - &?;
    com = re.sub("&.*;", "", com)
    return com

def processthread(thread):
    "Break a thread down into words"
    #Data storage container
    words = []
    #Capture the subject of the thread
    if 'sub' in thread['posts'][0]:
        subject = thread['posts'][0]['sub']
        for word in breakdowngroup(subject):
            words.append(word)
    #Capture the Comments and Filenames of each post in the thread.
    for post in thread['posts']:
        if 'com' in post:
            processed_comment = processcomment(post['com'])
            for word in breakdowngroup(processed_comment):
                words.append(word)
        if 'filename' in post:
            filename = post['filename']
            for word in breakdowngroup(filename):
                words.append(word)
    #return the words
    return words

def breakdowngroup(group):
    "Break a string down to words, remove punctuation, tolowercase."
    words = group.split()
    for i, sts in enumerate(words):
        words[i] = sts.lower()
        words[i] = strip_punctuation(words[i])
    return words

# I stole this function from Quora.
# Yes, I'm ashamed.
def strip_punctuation(contaminatedstring):
    "strip punctuation"
    return ''.join(c for c in contaminatedstring if c not in punctuation)

def asimilate(thread, master):
    "Put thread data into the master database"
    for word in thread:
        if word in master:
            master[word] += 1
        else:
            master[word] = 1
    return master

def valsort(dat):
    "Sort a dictionary by values"
    return sorted(dat.items(), key=operator.itemgetter(1))

def main():
    "Runs other functions."
    indexjson = getindexjson()
    nums = getnums(indexjson)
    # a num is a thread index, used to get a thread with getthread()
    print("Sleeping for 1 sec between API requests...")
    sleep(1)
    masterdata = {}
    for numy in nums:
        thread = getthread(numy)
        threaddata = processthread(thread)
        masterdata = asimilate(threaddata, masterdata)
    masterdata = valsort(masterdata)
    for pair in masterdata:
        print(str(pair[0])+":"+str(pair[1]))

if __name__ == '__main__':
    main()
