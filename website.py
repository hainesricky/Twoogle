import cgi

from google.appengine.api import users

import webapp2
from tweetcollector import TweetCollector

MAIN_PAGE_HTML = """\
<html>
<head>
<link href="/stylesheets/special.css" rel="stylesheet" type="text/css" />
</head>
<body>
<div class="main">
<br/><br/><br/><br/><br/><br/>
<h1 align="center" class="test">Twoogle</h1>
<h2 align="center" class="subtext">The Twitter friend-finder</h2>

<p align="center">Enter your Twitter user name</p>

<form action="/results" method="post" align="center">
  <div><input type="text" name="content" size="45"></div>
  <div><input type="submit" value="Go"></div>
</form>
<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
</div>
</body>
</html>
"""


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write(MAIN_PAGE_HTML)


class Results(webapp2.RequestHandler):

    def post(self):
		try:
			tc = TweetCollector()
			user=cgi.escape(self.request.get('content'))
			recs = tc.UserInput(user)
			discussion= tc.discussionPartners
			commenters= tc.commenters
			active= tc.activeFollowers
			follower= tc.followerCount
			#Write html head
			self.response.write('<html><head><link href="stylesheets/special.css" rel="stylesheet" type="text/css"></head>')
			#Write html body opening
			self.response.write('<body><h1 align="center" style="margin-top: 50px;">Results for <a href="http://www.twitter.com/'+str(user)+'">'+str(user)+'</a></h1><div class="results">')
			
			#Write body subsections
			self.response.write('<div style="margin-left: 10px;"><h2 class="results">Top Recommended People to Follow</h2>')
			if(recs is None):
				self.response.write('<p style="margin-left: 40px;">No recommendations found, please try again later!</p>')
			else:
				if(len(recs)==0):
					self.response.write('<p style="margin-left: 40px;">No recommendations found, please try again later!</p>')
				else:
					self.response.write('<p style="margin-left: 40px;">')
					y=1
					for person in recs:
						self.response.write(str(y)+'. <a href="http://www.twitter.com/'+str(person)+'">'+str(person)+'</a><br>')
						y+=1
						if(y==6):
							break
					self.response.write('</p>')
			
			self.response.write('<h2 class="results">Top Discussion Partners</h2>')
			if(len(discussion)>0):
				self.response.write('<p style="margin-left: 40px;">')
				x=1
				for person in discussion:
					self.response.write(str(x)+'. <a href="http://www.twitter.com/'+str(person)+'">'+str(person)+'</a><br>')
					x+=1
					if(x==6):
						break
				self.response.write('</p>')
			else:
				self.response.write('<p style="margin-left: 40px;">No discussion partners found, please try again later!</p>')
			
			self.response.write('<h2 class="results">Follower Breakdown</h2><div style="margin-left: 40px;">')

			self.response.write('<p>'+str(follower)+' <a href="http://www.twitter.com/'+str(user)+'/followers">followers</a></p>')
			self.response.write('<p>'+str(len(discussion))+' discussion partners</p>')
			self.response.write('<p>'+str(len(commenters))+' commenters</p>')
			self.response.write('<p>'+str(len(active))+' active followers</p>')
			
			#Close body
			self.response.write('</div></div></body></html>')
		except Exception as e:
			self.response.write('<html><head><link href="stylesheets/special.css" rel="stylesheet" type="text/css"></head>')
			self.response.write('<body><div class="main"><br/><br/><br/><br/><br/><br/><h1 align="center" style="margin-top: 50px;" class="test">Whoops!</a></h1></body>')
			self.response.write('<div><h2 class="subtext" align="center">An error occured</h2>')
			self.response.write('<p align="center">'+str(e.message)+'</p>')
			self.response.write('<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>')
			self.response.write('</div></div></body></html>')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/results', Results),

], debug=True)
