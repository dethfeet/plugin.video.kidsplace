#THX to conorbranagan for the playback code
# -> https://github.com/conorbranagan/xbmc-plugins/blob/master/plugin.video.pbs_kids/addon.py

import xbmc, xbmcgui, xbmcplugin
import helper
from xml.dom import minidom
import urllib, re
import urllib2, sys

thisChannel = "pbskidsgo"

thisPlugin = int(sys.argv[1])

baseLink = ""
baseLinkNav = ""

customBoolean = "isGo"
affiliate = "PBS KIDS GO NATIONAL"
player = "KidsGOplayer"
playerQuery = "&query=CustomBoolean|%s|true" % (customBoolean)

customBoolean = "isPreschool"
affiliate = "PBS KIDS NATIONAL"
player = "PreKplayer"
playerQuery = "&query=CustomBoolean|%s|true" % (customBoolean)

#customBoolean = "isPreschool"
#affiliate = "ARUR"
#player = "ProducerPlayer"
#playerQuery = "&query=KeywordsSearch|videoPLAYER"

mainPageLink = "http://pbs.feeds.theplatform.com/ps/API/PortalService/2.2/getCategoryList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&startIndex=1&endIndex=50&query=customText|CategoryType|%s&query=CustomBoolean|%s|true&query=HasReleases&field=fullTitle&customField=thumbnail2URL"
videoPageLink = "http://pbs.feeds.theplatform.com/ps/API/PortalService/2.2/getReleaseList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&startIndex=%s&endIndex=%s&sortField=airdate&sortDescending=true&query=Categories|%s&field=title&field=airdate&field=length&field=description&field=language&field=thumbnailURL&field=URL&field=PID&field=contentID&contentCustomField=IsClip&contentCustomField=isGame_header&contentCustomField=TV_RATING&contentCustomField=Episode_Title&param=affiliate|%s&param=player|%s%s"

def mainPage():
    menu_link = mainPageLink % ("Show",customBoolean)
    helper.addDirectoryItem("Shows",{"channel":thisChannel, "action":"subPageXml", "link":menu_link})
    
    menu_link = mainPageLink % ("Channel",customBoolean)
    helper.addDirectoryItem("Channels",{"channel":thisChannel, "action":"subPageXml", "link":menu_link})

    menu_link = ""
    helper.addDirectoryItem("New",{"channel":thisChannel, "action":"videoPageXml", "link":menu_link})

    helper.endOfDirectory()
    
def subPageXml(link):
    xmlPage = helper.load_page(link)
    xmlDom = minidom.parseString(xmlPage)
    for category in xmlDom.getElementsByTagName("Category"):
        menu_name = category.getElementsByTagName("fullTitle")[0].firstChild.data
        menu_link = videoPageLink % ("1","20",menu_name,affiliate,player,playerQuery)
        menu_img = ""
        menuImgItem = category.getElementsByTagName("CustomDataElement")[0].getElementsByTagName("value")[0].firstChild
        if menuImgItem is not None:
            menu_img = menuImgItem.data
        parameters = {"channel":thisChannel, "action":"videoPageXml", "link":menu_link, "start":"1","name":menu_name}
        helper.addDirectoryItem(menu_name,parameters,menu_img,folder=True)
    
    helper.endOfDirectory()

def videoPageXml(link, start, showName):
    xmlPage = helper.load_page(link)
    xmlDom = minidom.parseString(xmlPage)
    for release in xmlDom.getElementsByTagName("Release"):
        titles = release.getElementsByTagName("title")
        menu_name = release.getElementsByTagName("title")[len(titles)-1].firstChild.data
        clip = ""
        for customData in release.getElementsByTagName("CustomDataElement"):
            if customData.getElementsByTagName("title")[0].firstChild.data == "Episode_Title":
                if customData.getElementsByTagName("value")[0].firstChild is not None:
                    menu_name = customData.getElementsByTagName("value")[0].firstChild.data
            if customData.getElementsByTagName("title")[0].firstChild.data == "IsClip":
                if customData.getElementsByTagName("value")[0].firstChild.data == "true":
                    clip = " (Clip)"
        menu_name = menu_name+clip
        menu_link = release.getElementsByTagName("URL")[0].firstChild.data
        menu_img = ""
        if release.getElementsByTagName("thumbnailURL")[0].firstChild is not None:
            menu_img = release.getElementsByTagName("thumbnailURL")[0].firstChild.data
        menu_duration = str(int(release.getElementsByTagName("length")[0].firstChild.data)/1000/60)
        parameters = {"channel":thisChannel, "action":"playVideo", "link":menu_link}
        helper.addDirectoryItem(menu_name,parameters,menu_img,folder=False,duration=menu_duration)
    
    total_count = int(xmlDom.getElementsByTagName("totalCount")[0].firstChild.data)
    if int(start)+20<total_count:
        menu_link = videoPageLink % (str(int(start)+20),str(int(start)+40),showName,affiliate,player,playerQuery)
        parameters = {"channel":thisChannel, "action":"videoPageXml", "link":menu_link, "start":str(int(start)+20),"name":showName}
        helper.addDirectoryItem("Show more",parameters)
    helper.endOfDirectory()

class PBSRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise Exception(headers['location'])

    http_error_301 = http_error_303 = http_error_307 = http_error_302

def playVideo(link):
    proxy_address = xbmcplugin.getSetting(thisPlugin,'proxy_address')
    proxy_port = xbmcplugin.getSetting(thisPlugin,'proxy_port')
    
    print link

    if len(proxy_address):
        us_proxy = "http://"+proxy_address+":"+proxy_port
        print 'Using proxy: ' + us_proxy
        proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
        opener = urllib2.build_opener(proxy_handler, PBSRedirectHandler)
        urllib2.install_opener(opener)
    else:
        opener = urllib2.build_opener(PBSRedirectHandler)
        urllib2.install_opener(opener)
    
    streamUrl = ""
    
    try:
        # some refs are a redirect to the correct video url and
        # some refs return xml info about correct video url
        response = urllib2.urlopen(link)
        # only reach this point if no redirect
        data = response.read()
        response.close()
        dom = minidom.parseString(data)
        xmlnode = dom.getElementsByTagName('url')[0]
        streamUrl = xmlnode.firstChild.nodeValue.replace('<break>', '')
    except Exception, e:
        streamUrl = str(e).replace('<break>', ' playpath=MP4:') # This is an odd way of doing this..

    helper.setResolvedUrl(streamUrl)

    
params = helper.get_params()
if len(params) == 1:
    mainPage()
else:
    if params['action'] == "subPageXml":
        subPageXml(urllib.unquote(params['link']))
    if params['action'] == "videoPageXml":
        videoPageXml(urllib.unquote(params['link']),params['start'],urllib.unquote(params['name']))
    if params['action'] == "playVideo":
        playVideo(urllib.unquote(params['link']))
