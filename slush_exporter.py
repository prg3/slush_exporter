#!/usr/bin/env python2.7

import tornado, tornado.web, tornado.options
import datetime
import json, urllib2

SLUSHPOOLURL="https://slushpool.com/stats/json/"
SLUSHAPIURL="https://slushpool.com/accounts/profile/json/"

class HelpHandler(tornado.web.RequestHandler):
	def get(self):
		self.write( "Use /metrics with ?token=API_TOKEN\n")

def getAPIData(token):
	data = {}
	print token
	print (SLUSHAPIURL + token)
	data['account'] = json.loads(urllib2.urlopen(SLUSHAPIURL + token).read())
	data['pool'] = json.loads(urllib2.urlopen(SLUSHPOOLURL + token).read())
	return data

def formatOutput(data):
	tags = '"username="%s"'%(data['account']['username'])
	string = ""
	string += 'slushpool_account_unconfirmed{%s} %s\n'%(tags, data['account']['unconfirmed_reward'])
	string += 'slushpool_account_confirmed{%s} %s\n'%(tags, data['account']['confirmed_reward'])
	string += 'slushpool_account_estimated{%s} %s\n'%(tags, data['account']['estimated_reward'])
	string += 'slushpool_account_hashrate{%s} %s\n'%(tags, data['account']['hashrate'])
	string += 'slushpool_account_send_threshold{%s} %s\n'%(tags, data['account']['send_threshold'])
	for worker in data['account']['workers']:
		string += 'slushpool_account_worker_hashrate{%s,worker="%s"} %s\n'%(tags, worker, data['account']['workers'][worker]['hashrate'])
		string += 'slushpool_account_worker_score{%s,worker="%s"} %s\n'%(tags, worker, data['account']['workers'][worker]['score'])
		string += 'slushpool_account_worker_shares{%s,worker="%s"} %s\n'%(tags, worker, data['account']['workers'][worker]['shares'])
		if data['account']['workers'][worker]['alive']:
			string += 'slushpool_account_worker_alive{%s,worker="%s"} 1\n'%(tags, worker)
		else:
			string += 'slushpool_account_worker_alive{%s,worker="%s"} 0\n'%(tags, worker)
	try:
		[hr, mn, ss] = [int(x) for x in data['pool']['round_duration'].split(':')]
		roundtime = datetime.timedelta(hours=hr, minutes=mn, seconds=ss).seconds
	except:
		roundtime = 0

	for i in ["b10", "b250", "7", "30", "1"]: 
		string += 'slushpool_pool_luck{%s,period="%s"} %s\n'%(tags, i, data['pool']['luck_' + i])
	string += 'slushpool_pool_round_time{%s} %s\n'%(tags, roundtime)
	string += 'slushpool_pool_cdf{%s} %s\n'%(tags, data['pool']['shares_cdf'])
		
	return(string)
	
	

class MetricsHandler(tornado.web.RequestHandler):
	def get(self):
	        self.set_header("Content-Type", 'text/plain; charset="utf-8"')
		token=self.get_argument("token", None, True)
		data = getAPIData(token)
		self.write(formatOutput(data))
		

def main():
	tornado.options.parse_command_line()
	application = tornado.web.Application([
		(r"/", HelpHandler),
		(r"/metrics", MetricsHandler)

	])
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(9155)
	tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
	main()
