import tweepy
import json
import sys


class TweetCollector():
    def __init__(self):
		self.consumer_key = 'zLAoFmR5s13SkctUc9syQQ'
		self.consumer_secret = 'eWjJT0iM3MSGMhhxFUiV1cXErvIchSrq8iV2ODKI'
		self.access_token_key = '1972346221-2KMJKozzJqX35h3cZIKfA23YTQ8hDhkfM7cXkuB'
		self.access_token_secret = 'kmaQqGHJ6B75x6DPbum1jrsd6kUrNqRVXkOprLkFn4TS9'

		self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		self.auth.set_access_token(self.access_token_key, self.access_token_secret)
		self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())

		self.followers={}
		self.followerCount=0
		self.docs={}
		self.userMentions={}
		self.discussionPartners=[]
		self.activeFollowers=[]
		self.commenters=[]
		self.potentalRecs=[]
		
		
    def check_api_rate_limit(self, sleep_time):
        try:
            rate_limit_status = self.api.rate_limit_status()
        except Exception as error_message:
            if error_message['code'] == 88:
                print "Sleeping for %d seconds." %(sleep_time)
                print rate_limit_status['resources']['statuses']
                time.sleep(sleep_time)

        while rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'] < 10:
            print "Sleeping for %d seconds." %(sleep_time)
            print rate_limit_status['resources']['statuses']
            time.sleep(sleep_time)
            rate_limit_status = self.api.rate_limit_status()
        #print rate_limit_status['resources']['statuses']['/statuses/user_timeline']

		
    def UserInput(self, name):
		if not name:
			raise Exception('Specify a user name')
		try:
			self.api.get_user(name)
		except:
			raise Exception('Username is invalid!')
			
		self.CollectData(name)
		self.SortData(name)
		recs=self.FindRecs(name)
		self.followers=self.api.followers_ids(name)
		self.followerCount=len(self.followers['ids'])
		return recs
	
    def IsRetweetOfUser(self,tweet,user):
        if((tweet['text'].encode('utf-8')).find("RT @"+str(user),0,4+len(str(user)))>-1):
            return True
        return False

    def IsRetweet(self, tweet):
        if((tweet['text'].encode('utf-8')).find("RT",0,2)>-1):
            return True
        return False

	
	
	
    def FindOrMakeUserEntry(self,key):
        #The entries of the dictionary mean, respectively:
        #the times the user has mentioned them, the times they've mentioned the user, the number of times the user has retweeted them, and the number of times they've retweeted the user
        return self.userMentions.setdefault(key,{'user_mention':0,'mention_user':0,'user_retweet':0,'retweet_user':0})

    def CollectData(self, user):
       results=self.api.search(q='@'+user, count=200, leng='en')
       print "Found "+str(len(results['statuses']))+" tweets mentioning user "+str(user)
       retweetCount=0
       for tweet in results['statuses']:
            tweeter=tweet['user']['screen_name'].encode('utf-8')

            if self.IsRetweetOfUser(tweet,user):
                self.FindOrMakeUserEntry(tweeter)['retweet_user']+=1
                retweetCount+=1
            else:
                self.FindOrMakeUserEntry(tweeter)['mention_user']+=1
       print str(retweetCount)+" of them were retweets of the user"
       timeline=self.api.user_timeline(screen_name=user, count=200)
       for tweet in timeline:
           try:
                if self.IsRetweet(tweet):
                    nameEnd=(tweet['text'].encode('utf-8')).find(':')
                    retweeted=tweet['text'][4:nameEnd].encode('utf-8')

                    self.FindOrMakeUserEntry(retweeted)['user_retweet']+=1
                else:
                    for user in tweet['entities']['user_mentions']:
                        self.FindOrMakeUserEntry(user['screen_name'])['user_mention']+=1
           except:
                print "Skipping tweet:"
                print tweet['text'].encode('utf-8')
                continue
       print "Found "+str(len(timeline))+" tweets from user"
       print "In all combined tweets, "+str(len(self.userMentions))+" different users were mentioned or mentioned the user"
       
    def SortData(self, mainUser):
        for user in self.userMentions:
            userInfo=self.userMentions[user]
            #If a lot of back and forth, discussion partner. Using VERY rough guidelines right now.
            if userInfo['user_mention'] > 5 and userInfo['mention_user'] > 5:
                self.discussionPartners.append(user)
                friends=self.api.show_friendship(source_screen_name=mainUser, target_screen_name=user)['relationship']['source']['followed_by']
                if not bool(friends):
                    self.potentalRecs.append(user)
                continue
            #If a lot of one-way (him->you), commenter
            if userInfo['mention_user'] > 5:
                self.commenters.append(user)
                continue
            #If the user has been interacting with THEM, they are a potential recommendation if they are not a follower
            if userInfo['user_mention'] > 2:
               friends=self.api.show_friendship(source_screen_name=mainUser, target_screen_name=user)['relationship']['source']['followed_by']
               if not bool(friends):
                   self.potentalRecs.append(user)
            #For now, if otherwise AND has some recent activity towards you -> active follower
            self.activeFollowers.append(user)

            #If on friends list and not active follower, passive follower
        print "Follower breakdown for "+mainUser
        print str(len(self.discussionPartners))+" discussion partners"
        print str(len(self.commenters))+" commenters"
        print str(len(self.activeFollowers))+" active followers"
        print "Finding recommendations...."

    def FindRecs(self, mainUser):
        checkCount=0
        for user in self.discussionPartners:
            recs=self.CollectPartnerData(user,mainUser)
            self.potentalRecs.extend(recs)
            checkCount+=1
            if checkCount > 50:
                break

            return self.potentalRecs

    def CollectPartnerData(self, minorUser, mainUser):
		results=self.api.search(q='@'+minorUser, count=200, leng='en')
		userList={}
		for tweet in results['statuses']:
			tweeter=tweet['user']['screen_name'].encode('utf-8')

			if self.IsRetweetOfUser(tweet,minorUser):
				pass
			else:
				userList.setdefault(tweeter,{'user_mention':0,'mention_user':0,'id':0})['mention_user']+=1
				userList[tweeter][id]=tweet['user']['id']
		timeline=self.api.user_timeline(screen_name=minorUser, count=200)
		for tweet in timeline:
		   try:
				if self.IsRetweet(tweet):
				   pass
				else:
					for user in tweet['entities']['user_mentions']:
						userList.setdefault(user['screen_name'].encode('utf-8'),{'user_mention':0,'mention_user':0,'id':0})['user_mention']+=1
						userList[user['screen_name'].encode('utf-8')]['id']=tweet['entities']['user_mentions']['id']
		   except:
				pass

		recs=[]
		for user in userList:
			userInfo=userList[user]
			#If a lot of back and forth, discussion partner. Using VERY rough guidelines right now.
			if userInfo['user_mention'] >= 5 and userInfo['mention_user'] >= 5 and user!=mainUser:
				friends=self.api.show_friendship(source_screen_name=mainUser.encode('utf-8'), target_screen_name=user.encode('utf-8'))['relationship']['source']['followed_by']
				if not bool(friends):
					recs.append(user)
			
		return recs

def main():
    tc = TweetCollector()
    tc.check_api_rate_limit(900)
    tc.UserInput()

if __name__ == "__main__":
    main()
