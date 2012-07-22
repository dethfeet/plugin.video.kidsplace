import helper
from xml.dom import minidom
import urllib
import re

thisChannel = "pbskids"

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

def playVideo(link):
    streamUrl = helper.load_page(link,True, getRedirect=True)
    
    if not streamUrl == link:
        streamUrl = streamUrl.replace("<break>"," playpath=MP4:")
    else:
        streamPage = helper.load_page(link,True)
        extractUrl = re.compile("<url>(.*?)</url>")
        streamUrl = extractUrl.search(streamPage).group(1)
        streamUrl = streamUrl.replace("&lt;","<")
        streamUrl = streamUrl.replace("&gt;",">")
        streamUrl = streamUrl.replace("&amp;","&")
        streamUrl = streamUrl.replace("<break>"," playpath=")
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
