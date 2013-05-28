import xbmcplugin, xbmcgui
import urllib, sys, re
import helper
import json
import pprint

import brightcovePlayer

height = 1080

thisChannel = "zui"
baseLink = "http://zui.com"

def mainPage():
    page = helper.load_page(baseLink + "/videos")
    
    heroCats = re.compile("<ul id=\"hero_cats\">(.*?</ul><ul id=\"more_cats\">.*?)</ul>", re.DOTALL).search(page).group(1)
    
    items = re.compile("<a href=\"(/videos/category/(.*?))\" class=\".*?\"><span>(.*?)</span></a>").finditer(heroCats)
    
    helper.addDirectoryItem("All", {"channel":thisChannel, "action":"showCategory", "link":"/videos"})
    
    for category in items:
        catName = category.group(3)
        catLink = category.group(1)
        catImg = baseLink + "/assets/icons/cats/" + category.group(2).replace("+", "_") + "_normal.png"
        helper.addDirectoryItem(catName, {"channel":thisChannel, "action":"showCategory", "link":catLink}, catImg)

    helper.endOfDirectory()

def showCategory(link):
    page = helper.load_page(baseLink+urllib.unquote(link))

    extractVideos = re.compile("<div class=\"peepshow\">.*?<a href=\"(.*?)\">(.*?)</a>.*?<img.*?src=\"(.*?)\".*?<p>(.*?)</p>",re.DOTALL)
    
    for video in extractVideos.finditer(page):
        vidName = video.group(2)
        vidName = helper.removeHtmlSpecialChars(vidName)
        vidLink = video.group(1)
        vidImg = video.group(3)
        vidPlot = video.group(4)
        parameters = {"channel":thisChannel, "action":"playVideo", "link":vidLink}
        helper.addDirectoryItem(vidName, parameters, vidImg, False, plot=vidPlot)
        
    extractNextPage = re.compile("<li class=\"next\"><a href=\"(.*?)\" rel=\"next\">Next")
    
    nextPage = extractNextPage.search(page)
    
    if nextPage is not None:
        helper.addDirectoryItem("Show more", {"channel":thisChannel, "action":"showCategory", "link":nextPage.group(1)})
    
    helper.endOfDirectory()

def playVideo(link):
    page = helper.load_page(baseLink + urllib.unquote(link))
    
    extractYouTubeId = re.compile("<div data-youtube=\"(.*?)\" id=\"yt_video\">")
    
    youTubeInfo = extractYouTubeId.search(page)
    
    if youTubeInfo is not None:
        youTubeId = youTubeInfo.group(1)
        streamUrl = "plugin://plugin.video.youtube/?action=play_video&videoid=" + youTubeId 
        helper.setResolvedUrl(streamUrl)
    else:
        #bitsontherun
        extractVideoId = re.compile("<div id=\"container\" style=\"display: none;\"><script type=\"text/javascript\" src=\"(http://content.bitsontherun.com/players/.*?-.*?.js)\"></script></div>")
        videoInfo = extractVideoId.search(page)
        if videoInfo is not None:
            jsURL = videoInfo.group(1)            
            bitsontherunJS = helper.load_page(jsURL)
            extractVideoUrl = re.compile("botrObject.swf\(\n\t\".*?\",\n\t\".*?\",\n\t\".*?\",\n\t\"(.*?)\",")
            videoUrlInfo = extractVideoUrl.search(bitsontherunJS)
            videoUrl = videoUrlInfo.group(1);
            #videoUrl = videoUrl.replace("conversions/","http://v.jwpcdn.com/")
            helper.setResolvedUrl(videoUrl)

params = helper.get_params()
if len(params) == 1:
    mainPage()
else:
    if params['action'] == "showCategory":
        showCategory(params['link'])
    if params['action'] == "playVideo":
        playVideo(params['link'])
