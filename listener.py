#basic schedule job to use summaryInfo to summarise data, delete data and tweet summary plot

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import os
import io
from datetime import datetime, date, timedelta
import time
import random
import copy
import sys
sys.path.insert(0, '../configs/')
import configSettings_ao as configSettings
sys.path.insert(0, '../whatAmITalkingAbout/')
import analytics
sys.path.insert(0, '../roboTwitter/')
import plotInfo
import argumentClass


start_time = time.time() #grabs the system time
keyword_list = ['OracleAuto'] #track list

def tweet_image(filename, message):
    api=configSettings.get_api()
    #api.update_status(status=message)
    api.update_with_media(filename, status=message)
    return

def WAITA(who,options):
    print ">>> listener:WAITA: inside:",who
    argDict={'who':who, 'start':(datetime.now() - timedelta(1)), 'end':datetime.now(), 'pages':"-1", 'topics':"nhs"}
    print ">>> listener:WAITA: argDict:",argDict
    topArr=analytics.GleanTwitter(argDict)
    print ">>> listener:WAITA: topArr:",len(topArr)
    plotName=analytics.PlotFreq(topArr,False,"plots/"+who+"_"+datetime.now().strftime("%Y-%m-%d")+"_"+str(random.uniform(1,100))+".png")
    print ">>> listener:WAITA: plotName:",plotName
    return plotName

def MeasSum(options="NYS"):
    print ">>> listener:MeasSum:"
    argDict=copy.deepcopy(argumentClass.templatePlotDict)
    argDict['start']=(datetime.now() - timedelta(1))
    argDict['end']=datetime.now()
    argDict['save']="True"
    argDict['saveName']="plots/MeasSum_"+datetime.now().strftime("%Y-%m-%d")+".png"
    print ">>> listener:MeasSum: argDict:",argDict
    twitterInfo=plotInfo.GleanTwitter(argDict)
    print ">>> listener:MeasSum: twitterInfo:",len(twitterInfo)
    plotName=plotInfo.PlotData(argDict,twitterInfo)
    print ">>> listener:MeasSum: plotName:",plotName
    return plotName


def TextCommand(txt, who="OracleAuto"):

    for t in txt.split(' '):
        if "WAITA" in t or "waita" in t:
            print ">>> listener:TextCommand: processing talk"
            plotName=WAITA(who,t[t.find('(')+1:t.find(')')])
            print ">>> listener:TextCommand: file to tweet:",plotName
            tweet_image(plotName,"@"+who+" this is what you're talking about...")
        elif "easSum" in t:
            print ">>> listener:TextCommand: processing talk"
            plotName=MeasSum()
            print ">>> listener:TextCommand: file to tweet:",plotName
            tweet_image(plotName,"@"+who+" some stats")
        elif "other" in t:
            print "in other"
            elArr=["hydorgen.jpg","helium.jpg","lithium.jpg"]
            plotName=elArr[random.uniform(0,len(elArr)-1)]
            print ">>> listener:TextCommand: file to tweet:",plotName
            tweet_image(plotName,"@"+who+" it's elemental")
        else:
            print "unknown command:",t

    return

#Listener Class Override
class listener(StreamListener):
    
    def __init__(self, start_time, time_limit=60):
        
        self.time = start_time
        self.limit = time_limit
        self.tweet_data = []
    
    def on_data(self, data):
        
        #saveFile = io.open('raw_tweets.json', 'a', encoding='utf-8')
        
        while True: #(time.time() - self.time) < self.limit:
            
            try:
                self.tweet_data.append(data)
                stat_text=data.split(',')[3]
                stat_who=data.split(',')[14].split(':')[1].strip("\"")
                print "something happened("+stat_who+"):",stat_text
                TextCommand(stat_text, stat_who)
                return True
            
            
            except BaseException, e:
                print 'failed ondata,', str(e)
                time.sleep(5)
                pass



        '''
        saveFile = io.open('raw_tweets.json', 'w', encoding='utf-8')
        saveFile.write(u'[\n')
        saveFile.write(','.join(self.tweet_data))
        saveFile.write(u'\n]')
        saveFile.close()
        exit()
        '''

    def on_error(self, status):
        print status
        if status == 420:
            print "sleeping for ten minutes, starting:",str(datetime.now())
            time.sleep(10*60)

auth = OAuthHandler(configSettings.cfg['consumer_key'], configSettings.cfg['consumer_secret']) #OAuth object
auth.set_access_token(configSettings.cfg['access_token'], configSettings.cfg['access_token_secret'])


twitterStream = Stream(auth, listener(start_time, time_limit=200)) #initialize Stream object with a time out limit
twitterStream.filter(track=keyword_list, languages=['en'])  #call the filter method to run the Stream Object





