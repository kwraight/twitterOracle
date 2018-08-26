#basic schedule job to use summaryInfo to summarise data, delete data and tweet summary plot

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import os
import io
import analytics
from datetime import datetime, date, timedelta
import time
import random
import sys
sys.path.insert(0, '../configs/')
import configSettings_ao as configSettings



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


def TextCommand(txt, who="OracleAuto"):

    for t in txt.split(' '):
        if "WAITA" in t or "waita" in t:
            print ">>> listener:TextCommand: processing talk"
            plotName=WAITA(who,t[t.find('(')+1:t.find(')')])
            print ">>> listener:TextCommand: file to tweet:",plotName
            tweet_image(plotName,"@"+who+" this is what you're talking about...")
        elif "that" in t:
            print "in that"
            tweet_image("helium.jpg","@"+who+" it's elemental")
        elif "other" in t:
            print "in other"
            tweet_image("lithium.jpg","@red_hot_kenny it's elemental")
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
        
        while (time.time() - self.time) < self.limit:
            
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


auth = OAuthHandler(configSettings.cfg['consumer_key'], configSettings.cfg['consumer_secret']) #OAuth object
auth.set_access_token(configSettings.cfg['access_token'], configSettings.cfg['access_token_secret'])


twitterStream = Stream(auth, listener(start_time, time_limit=200)) #initialize Stream object with a time out limit
twitterStream.filter(track=keyword_list, languages=['en'])  #call the filter method to run the Stream Object





