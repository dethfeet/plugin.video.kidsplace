import urllib, re
import helper
import binascii, aes
import hmac
import random
import time
import operator

import xbmcgui

#Thanks to BlueCop's Hulu plugin for the playback code: 
#http://code.google.com/p/bluecop-xbmc-repo/source/browse/trunk/plugin.video.hulu

thisChannel = "4kidstv"
baseLink = "http://4kidstv.com"
huluLink = "http://s.hulu.com/select?video_id=%s&v=888324234&ts=1341832856&np=1&vp=1&enable_fa=1&device_id=D29F5DD18BB97A6C76FCECDF0F63A28D&pp=EDP&dp_id=Forkids&region=US&language=en&bcs=48ab872ad901a527012f39dcb29aa16f"

smildeckey = ['d6dac049cc944519806ab9a1b5e29ccfe3e74dabb4fa42598a45c35d20abdd28', '27b9bedf75ccA2eC']

def mainPage():
    page = helper.load_page(baseLink + "/shows")
    extractChannels = re.compile("<!--BEGIN ALPHABETICAL-->(.*?)<!--END ALPHABETICAL-->", re.DOTALL)
    extractChannel = re.compile("<a href=\"(.*?)\".*?src=\"(.*?)\" />(.*?)</a>", re.DOTALL)
    
    channels = extractChannels.search(page).group(1)
    
    for channel in extractChannel.finditer(channels):
        menu_link = baseLink + channel.group(1)
        menu_name = channel.group(3)
        menu_img = channel.group(2)
        parameters = {"channel":thisChannel, "action":"showVideos", "link":menu_link, "season":""}
        helper.addDirectoryItem(menu_name, parameters, menu_img)

    helper.endOfDirectory()

def showVideos(link, season=""):
	link = urllib.unquote(link)
	page = helper.load_page(link)
	
	if season == "":
		extractSeasons = re.compile("<h2.*?swapCSS\('(.*?)'.*?>(.*?)</a></h2>", re.DOTALL)
		for season in extractSeasons.finditer(page):
			menu_season = season.group(1)
			menu_name = season.group(2)
			parameters = {"channel":thisChannel, "action":"showVideos", "link":link, "season":menu_season}
			helper.addDirectoryItem(menu_name, parameters)			
	else:
		extractVideos = re.compile("<div id=\"" + season + "\".*?>(.*?)</div>", re.DOTALL)
		extractVideo = re.compile("href=\"(.*?)\".*?src=\"(.*?)\".*?<span class=\"pwraper-title\">(.*?)</span>.*?<span class=\"para\">(.*?)</span>.*?<strong>Air Date:</strong>  (.*?) .*?<strong>Time:</strong> (.*?)</span>", re.DOTALL)
		videos = extractVideos.search(page).group(1)
    
		for video in extractVideo.finditer(videos):
			menu_link = video.group(1)
			menu_name = video.group(3)
			menu_img = video.group(2)
			menu_plot = video.group(4)
			menu_date = video.group(5)
			menu_duration = video.group(6)
			parameters = {"channel":thisChannel, "action":"playVideo", "link":menu_link}
			helper.addDirectoryItem(menu_name, parameters, menu_img, folder=False, duration=menu_duration, plot=menu_plot, date=menu_date)
	helper.endOfDirectory()
       
def playVideo(link):
	link = baseLink + urllib.unquote(link)
	page = helper.load_page(link)
	extractVideoId = re.compile("NewSite.videoPlayerComponent.playVideo\(([0-9]*)\);")
	extractVideoIdItem = extractVideoId.search(page)
	if extractVideoIdItem is not None:
		videoId = extractVideoIdItem.group(1)
		parameters = {'video_id'  : videoId,
					'v'         : '888324234',
					'ts'        : str(int(time.mktime(time.gmtime()))),
					'np'        : '1',
					'vp'        : '1',
					'enable_fa' : '1',
					'device_id' : makeGUID(),
					'pp'        : 'Desktop',
					'dp_id'     : 'Hulu',
					'region'    : 'US',
					'ep'        : '1',
					'language'  : 'en'
					}

		smilUrl = 'http://s.hulu.com/select?'
		for item1, item2 in parameters.iteritems():
			smilUrl += item1 + '=' + item2 + '&'
		smilUrl += 'bcs=' + content_sig(parameters)
        smilPage = helper.load_page(smilUrl, True)
        smilPage = helper.load_page(smilUrl)
        decr = aes.decryptData(binascii.unhexlify(smildeckey[0]), smildeckey[1] + binascii.unhexlify(smilPage))

        if decr.find("type=\"anonymous_proxy\"") >= 0:
            xbmcgui.Dialog().ok('Proxy Detected', 'Based on your IP address we noticed', 'you are trying to access Hulu', 'through an anonymous proxy tool')
            return False
        
        extractVideo = re.compile("<video server=\"(.*?)\" stream=\"(.*?)\" token=\"(.*?)\".*?height=\"([0-9]*)\".*?cdn=\"akamai\"")
       
        height = 0
        for video in extractVideo.finditer(decr):
            streamHeight = int(video.group(4))
            if streamHeight > height:
                height = streamHeight
                server = video.group(1)
                stream = video.group(2)
                token = video.group(3)
        
        if height == 0:
            xbmcgui.Dialog().ok('No Video Streams','SMIL did not contain video links','Geo-Blocked')
            return False
        
        appName = server[server.find("/",8)+1:]
        
        appName += '?sessionid=sessionId&' + token
        stream = stream[0:len(stream)-4]
        finalUrl = server + "?sessionid=sessionId&" + token + " app=" + appName
        
        SWFPlayer = 'http://download.hulu.com/huludesktop.swf'
        finalUrl += " playpath=" + stream + " swfurl=" + SWFPlayer + " pageurl=" + SWFPlayer + " swfvfy=true"

        helper.setResolvedUrl(finalUrl)

def content_sig(parameters):
    hmac_key = 'f6daaa397d51f568dd068709b0ce8e93293e078f7dfc3b40dd8c32d36d2b3ce1'
    sorted_parameters = sorted(parameters.iteritems(), key=operator.itemgetter(0))
    data = ''
    for item1, item2 in sorted_parameters:
        data += item1 + item2
    sig = hmac.new(hmac_key, data)
    return sig.hexdigest()

def makeGUID():
    guid = ''
    for i in range(8):
        number = "%X" % (int((1.0 + random.random()) * 0x10000) | 0)
        guid += number[1:]
    return guid
	
params = helper.get_params()
if len(params) == 1:
    mainPage()
else:
    if params['action'] == "showVideos":
        showVideos(params['link'], params['season'])
    if params['action'] == "playVideo":
        playVideo(params['link'])
