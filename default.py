import xbmcaddon
import sys
import os

import helper

addon = xbmcaddon.Addon(id='plugin.video.kidsplace')
addonpath = xbmc.translatePath( addon.getAddonInfo('path') )

channels = [
["4kidstv.com","4kidstv"],
["cbc.ca/kidscbc","cbcca"],
["hubworld.com","hubworld"],
["kidmango.com","kidmango"],
["kidswb.com","kidswb"],
["nickjr.com","nickjr"],
["pbskids.org","pbskids"],
["storylineonline.net","storylineonline"],
["treehousetv.com","treehousetv"],
["zui.com","zui"],
]

def mainPage():
	for channel in channels:
		channelPic = os.path.join(addonpath,'resources','images',channel[1]+'.png')
		helper.addDirectoryItem(channel[0],{"channel":channel[1]}, channelPic)
	helper.endOfDirectory()

if not sys.argv[2]:
    mainPage()
else:
	global params
	params = helper.get_params()
	importChannel = "channels."+params['channel']
	channel = __import__(importChannel)
