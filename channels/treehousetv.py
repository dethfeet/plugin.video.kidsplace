import urllib, re, json
import helper

import brightcovePlayer

thisChannel = "treehousetv"
baseLink = "http://media.treehousetv.com/"

playerKey = "AQ~~,AAAAocwue4k~,UrRkTX6e9GTh6MSuPZQSC42qoIqyrzCP"

height = 1080
const = "52efa4bed1a5ee74e256c9eb6a9be758a6a9b7d1"
playerID = 904944191001
publisherID = 694915333001

def mainPage():
    showSubMenu()
    
def showSubMenu(level1=-1):
    page = helper.load_page(baseLink)
    mainMenu = extractMenu(page)
    
    if level1 == -1:
        menu = mainMenu
    else:
        menu = mainMenu[int(level1)]['children']
    
    counter = 0
    for menuItem in menu:
        menu_name = menuItem['name'];
        
        menu_link = menuItem['link'];
        if len(menuItem['children']):
            helper.addDirectoryItem(menuItem['name'], {"channel":thisChannel, "action" : "showSubMenu", "link": counter})   
        else:        
            helper.addDirectoryItem(menuItem['name'], {"channel":thisChannel, "action" : "showVideos", "link": menu_link})
        counter = counter + 1
    
    helper.endOfDirectory()
    

def extractMenu(parent=None):
    page = helper.load_page(baseLink)
    
    extractChannels = re.compile("<div id=\"video-navigation\">(.*?)</div>",re.DOTALL)
    extractChannel = re.compile("<li.*?href=\"\?c=(.*?)\">(.*?)</a>")
    
    channels = extractChannels.search(page).group(1)
    
    channels = channels.replace("</li>","</li>\n")
    channels = channels.replace("</a>","</a>\n")
    
    menuList = []
    parent = -1;
    hasParent = False
    for line in channels.split("\n"):
        if line.find("<ul class=\"level_1\">") > -1:
            hasParent = True
        
        channel = extractChannel.search(line)
        if channel is not None:
            if not hasParent:
                parent = parent + 1
                menuList.append({"name" : channel.group(2), "link" : channel.group(1), "children" : []})
            else:
                menuList[parent]['children'].append({"name" : channel.group(2), "link" : channel.group(1), "children" : []})
        
        if line.find("</ul>") > -1:
            hasParent = False

    return menuList
    

def showVideos(link):
    link ="http://media.treehousetv.com/videos.ashx?c="+urllib.unquote(link)
    page = helper.load_page(link)
    data = json.loads(page)
        
    for video in data:
        menu_link = video["Id"]
        menu_name = video["Name"]
        menu_img = video["ThumbnailURL"]
        parameters = {"channel":thisChannel,"action":"playVideo","link":menu_link}
        helper.addDirectoryItem(menu_name, parameters, menu_img, folder=False)

    helper.endOfDirectory()
       
def playVideo(videoPlayer):
    stream = brightcovePlayer.play(const, playerID, videoPlayer, publisherID, playerKey)
    
    rtmpbase = stream[1][0:stream[1].find("&")]
    playpath = stream[1][stream[1].find("&") + 1:]
    finalurl = rtmpbase + ' playpath=' + playpath
    
    helper.setResolvedUrl(finalurl)

params = helper.get_params()
if len(params) == 1:
    mainPage()
else:
    print params['action']
    if params['action'] == "showSubMenu":
        showSubMenu(params['link'])
    if params['action'] == "showVideos":
        showVideos(params['link'])
    if params['action'] == "playVideo":
        playVideo(params['link'])