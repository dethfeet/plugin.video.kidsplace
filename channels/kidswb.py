import urllib, re, json
import helper

thisChannel = "kidswb"
baseLink = "http://www.kidswb.com"
metaframeLink = "http://metaframe.digitalsmiths.tv/v2/WBtv/assets/%s/partner/11?format=json"

def mainPage():
    page = helper.load_page(baseLink+"/video")
    extractChannels = re.compile("<ul id=\"channelCarousel_ul\">(.*?)</ul>",re.DOTALL)
    extractChannel = re.compile("<a href=\"(.*?)\".*?alt=\"(.*?)\" src=\"(.*?)\"",re.DOTALL)
    
    channels = extractChannels.search(page).group(1)
    
    for channel in extractChannel.finditer(channels):
        menu_link = baseLink+channel.group(1)
        menu_name = channel.group(2)
        menu_img = baseLink+channel.group(3)
        parameters = {"channel":thisChannel,"action":"showVideos","link":menu_link}
        helper.addDirectoryItem(menu_name, parameters, menu_img)

    helper.endOfDirectory()

def showVideos(link):
    page = helper.load_page(urllib.unquote(link))
    extractVideos = re.compile("<ul id=\"videoList_ul\">(.*?)</ul>",re.DOTALL)
    extractVideo = re.compile("<li class=\"vidItem [a-z]*\" id=\"video_(.*?)\".*?src=\"(.*?)\".*?<span id=\".*?\">(.*?)</span>",re.DOTALL)
    
    videos = extractVideos.search(page).group(1)
    
    for video in extractVideo.finditer(videos):
        menu_link = video.group(1)
        menu_name = helper.removeHtmlSpecialChars(video.group(3))
        menu_img = video.group(2)
        parameters = {"channel":thisChannel,"action":"playVideo","link":menu_link}
        helper.addDirectoryItem(menu_name, parameters, menu_img, folder=False)

    helper.endOfDirectory()
       
def playVideo(mediaId):
    link = metaframeLink % (mediaId)
    
    page = helper.load_page(link)
    data = json.loads(page)
    streamUrl = data['videos']['limelight700']['uri']
    
    helper.setResolvedUrl(streamUrl)

params = helper.get_params()
if len(params) == 1:
    mainPage()
else:
    if params['action'] == "showVideos":
        showVideos(params['link'])
    if params['action'] == "playVideo":
        playVideo(params['link'])