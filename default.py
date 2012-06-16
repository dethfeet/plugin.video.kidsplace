import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import urllib, urllib2
import re

import helper


addon = xbmcaddon.Addon(id='plugin.video.kidsplace')

channels = [
["hubworld.com","hubworld"],
["kidmango.com","kidmango"],
["nickjr.com","nickjr"],
]

def mainPage():
	for channel in channels:
		helper.addDirectoryItem(channel[0],{"channel":channel[1]})
	helper.endOfDirectory()

    
if not sys.argv[2]:
    mainPage()
else:
	global params
	params = helper.get_params()
	importChannel = "channels."+params['channel']
	channel = __import__(importChannel)
