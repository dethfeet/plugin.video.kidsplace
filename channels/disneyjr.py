import xbmc, xbmcgui
import helper
from xml.dom import minidom
import urllib, re

thisChannel = "disneyjr"

baseLink = "http://disney.go.com/disneyjunior/videos-episodes"
baseLinkNav = "http://disney.go.com/disneyjunior/data/leftNav?id=1809981"

def mainPage():
    menu_link = "http://disney.go.com/disneyjunior/data/tilePack?id=1815104&maxAmount=12&index=0"
    helper.addDirectoryItem("By Character",{"channel":thisChannel, "action":"subPageXml", "link":menu_link})
    
    menu_link = "http://disney.go.com/disneyjunior/data/tilePack?id=1815106&maxAmount=12&index=0"
    helper.addDirectoryItem("Full Episodes",{"channel":thisChannel, "action":"videoPageXml", "link":menu_link})

    menu_link = "http://disney.go.com/disneyjunior/data/tilePack?id=1815107&maxAmount=12&index=0"
    helper.addDirectoryItem("Short Videos",{"channel":thisChannel, "action":"videoPageXml", "link":menu_link})

    menu_link = "http://disney.go.com/disneyjunior/data/tilePack?id=1815108&maxAmount=12&index=0"
    helper.addDirectoryItem("Music Videos",{"channel":thisChannel, "action":"videoPageXml", "link":menu_link})

    helper.endOfDirectory()
    
def subPageXml(link, action="videoPage"):
    if action == "videoPage":
        nextAction = "subPageXml"
        isFolder = True
    elif action == "playVideo":
        nextAction = "videoPageXml"
        isFolder = False

    xmlPage = helper.load_page(link)
    xmlDom = minidom.parseString(xmlPage)
    for sprite in xmlDom.getElementsByTagName("sprite"):
        if sprite.getAttribute("class") == "com.disney.disneyjunior.classes.sprites.TileAsset video":
            menu_name = sprite.getElementsByTagName("text")[0].firstChild.data
            menu_name = helper.removeTags(menu_name)
            menu_link = sprite.getElementsByTagName("a")[0].getAttribute("href")
            menu_img = sprite.getElementsByTagName("img")[0].getAttribute("src")
            parameters = {"channel":thisChannel, "action":action, "link":menu_link}
            helper.addDirectoryItem(menu_name,parameters,menu_img,folder=isFolder)
    
    menuNode = xmlDom.getElementById("next")
    for a in xmlDom.getElementsByTagName("a"):
        if a.getAttribute("id") == "next":
            parameters = {"channel":thisChannel, "action":nextAction, "link":a.getAttribute("href")}
            helper.addDirectoryItem("Next page",parameters)
    
    helper.endOfDirectory()

def videoPage(link):
    page = helper.load_page(urllib.unquote(link))
    extractXml = re.compile("tileService: \"(.*?)\" };").search(page)
    if extractXml is not None:
        videoPageXml(extractXml.group(1).replace("%26","&"))

def videoPageXml(link):
    subPageXml(link, "playVideo")
        
def playVideo(link):
    page = helper.load_page(link,True)
    
    #print page
    #http://cdnapi.kaltura.com//api_v3/index.php?service=multirequest&action=null&kalsig=98219f70556227be25075e61f0505fbf&1%3Aservice=session&3%3Aks=%7B1%3Aresult%3Aks%7D&2%3Aaction=get&ignoreNull=1&3%3Aservice=uiconf&1%3Aaction=startWidgetSession&2%3Aks=%7B1%3Aresult%3Aks%7D&3%3Aid=6607922&3%3Aaction=get&clientTag=kdp%3Av3%2E5%2E53%2Eb&1%3Aexpiry=86400&1%3AwidgetId=%5F628012&2%3Aservice=widget&2%3Aid=%5F628012
    #http://cdnapi.kaltura.com//api_v3/index.php?service=multirequest&action=null&kalsig=b02f05c63e3bede1bb42077f37fb6b03&4%3Afilter%3AorderBy=%2BcreatedAt&4%3Afilter%3AobjectType=KalturaMetadataFilter&ks=YzRjYTUyNjI4ZDFjZjE1MDk2ZjZiZTgzMThiOGI1M2JmNDkxMmE3M3w2MjgwMTI7NjI4MDEyOzEzNDE0Njg3NTQ7MDsxMzQxMzgyMzU0LjEzNDk7MDt2aWV3Oio7Ow%3D%3D&3%3AcontextDataParams%3AstreamerType=auto&5%3Afilter%3AobjectType=KalturaCuePointFilter&1%3Aservice=baseentry&clientTag=kdp%3Av3%2E5%2E53%2Eb&4%3Afilter%3AobjectIdEqual=0%5Fm6d8wsry&4%3Afilter%3AmetadataObjectTypeEqual=1&4%3Aaction=list&ignoreNull=1&2%3Aservice=flavorasset&4%3Apager%3ApageSize=1&2%3Aaction=getWebPlayableByEntryId&2%3AentryId=0%5Fm6d8wsry&3%3AentryId=0%5Fm6d8wsry&5%3Aaction=list&1%3AentryId=0%5Fm6d8wsry&5%3Aservice=cuepoint%5Fcuepoint&1%3Aversion=%2D1&4%3Aservice=metadata%5Fmetadata&5%3Afilter%3AentryIdEqual=0%5Fm6d8wsry&1%3Aaction=get&3%3Aaction=getContextData&3%3AcontextDataParams%3AobjectType=KalturaEntryContextDataParams&3%3Aservice=baseentry&4%3Apager%3AobjectType=KalturaFilterPager
    #http://cdnapi.kaltura.com/index.php/partnerservices2/executeplaylist?uid=&format=8&partner_id=628012&subp_id=628012&playlist_id=0_l5kr39y0
    #http://cdnapi.kaltura.com/p/628012/sp/628012/playManifest/entryId/0_m6d8wsry/format/rtmp/protocol/rtmp/cdnHost/vp.disney.go.com/player/latest//storageId/1252/ks/YzRjYTUyNjI4ZDFjZjE1MDk2ZjZiZTgzMThiOGI1M2JmNDkxMmE3M3w2MjgwMTI7NjI4MDEyOzEzNDE0Njg3NTQ7MDsxMzQxMzgyMzU0LjEzNDk7MDt2aWV3Oio7Ow==/uiConfId/6607922/a/a.f4m?
    #http://cdnapi.kaltura.com//api_v3/index.php?service=multirequest&action=null&kalsig=b02f05c63e3bede1bb42077f37fb6b03&4%3Afilter%3AobjectType=KalturaMetadataFilter&ks=YzRjYTUyNjI4ZDFjZjE1MDk2ZjZiZTgzMThiOGI1M2JmNDkxMmE3M3w2MjgwMTI7NjI4MDEyOzEzNDE0Njg3NTQ7MDsxMzQxMzgyMzU0LjEzNDk7MDt2aWV3Oio7Ow%3D%3D&4%3Apager%3ApageSize=1&4%3Afilter%3AmetadataObjectTypeEqual=1&4%3Afilter%3AobjectIdEqual=0%5Fm6d8wsry&4%3Afilter%3AorderBy=%2BcreatedAt&5%3Afilter%3AobjectType=KalturaCuePointFilter&1%3Aaction=get&clientTag=kdp%3Av3%2E5%2E53%2Eb&ignoreNull=1&5%3Aaction=list&3%3AcontextDataParams%3AstreamerType=auto&4%3Aaction=list&2%3Aaction=getWebPlayableByEntryId&1%3Aservice=baseentry&4%3Aservice=metadata%5Fmetadata&5%3Afilter%3AentryIdEqual=0%5Fm6d8wsry&3%3Aaction=getContextData&3%3AentryId=0%5Fm6d8wsry&3%3Aservice=baseentry&3%3AcontextDataParams%3AobjectType=KalturaEntryContextDataParams&1%3AentryId=0%5Fm6d8wsry&5%3Aservice=cuepoint%5Fcuepoint&4%3Apager%3AobjectType=KalturaFilterPager&1%3Aversion=%2D1&2%3Aservice=flavorasset&2%3AentryId=0%5Fm6d8wsry
    #http://cdnapi.kaltura.com/p/628012/sp/628012/playManifest/entryId/0_m6d8wsry/format/rtmp/protocol/rtmp/cdnHost/vp.disney.go.com/player/latest//storageId/1252/ks/YzRjYTUyNjI4ZDFjZjE1MDk2ZjZiZTgzMThiOGI1M2JmNDkxMmE3M3w2MjgwMTI7NjI4MDEyOzEzNDE0Njg3NTQ7MDsxMzQxMzgyMzU0LjEzNDk7MDt2aWV3Oio7Ow==/uiConfId/6607922/a/a.f4m?
    #var tilePackVars = { configXMLPath: "http://disney.go.com/disneyjunior/data/videoConfig?cid=1944089" };
    extractId = re.compile("\{ configXMLPath: \"http://disney.go.com/disneyjunior/data/videoConfig\?cid=([0-9]*)\" \}").search(page)
    if extractId is not None:
        playlistLink = "http://disney.go.com/disneyjunior/data/videoPlaylist?cid="+extractId.group(1)
        xmlPage = helper.load_page(playlistLink)
        xmlPage = xmlPage.replace(" & "," &amp; ")
        xmlDom = minidom.parseString(xmlPage)
        
        playChapter = xmlDom.getElementsByTagName("chapter")[0]
        for chapter in xmlDom.getElementsByTagName("chapter"):
            if chapter.getAttribute("playFirst") == "true":
                playChapter = chapter
        
        playerItem = xbmcgui.ListItem(playChapter.getAttribute("title"))
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO);
        playlist.clear();
        
        for video in playChapter.getElementsByTagName("video"):
            streamUrl = video.getAttribute("streamurl")
            
            app = " app="+streamUrl[streamUrl.find("/",8)+1:]
            flashVer = " flashver=WIN%2010,3,181,26"
            #flashVer = ""
            swfUrl = " swfUrl=http://a.dolimg.com/en-US/disneyjunior/swf/videoplayerShell_MPF.swf swfVfy=1"
            pageUrl = " pageUrl="+link
            playpath = " playpath="+video.getAttribute("progurl")
            
            streamUrl = streamUrl[:streamUrl.find("/",8)] + swfUrl + app + pageUrl + flashVer + playpath
            print streamUrl
            
            helper.setResolvedUrl(streamUrl)
            #return False
            listItem = xbmcgui.ListItem(streamUrl, path=streamUrl);
            #listItem.setProperty("PlayPath", streamUrl);
            listItem.setProperty('IsPlayable', 'true')
            playlist.add(url=streamUrl, listitem=listItem)
        
        player = xbmc.Player()
        player.play(playlist, playerItem)
        return False
        
    
        
    
params = helper.get_params()
if len(params) == 1:
    mainPage()
else:
    if params['action'] == "subPageXml":
        subPageXml(urllib.unquote(params['link']))
    if params['action'] == "videoPage":
        videoPage(params['link'])
    if params['action'] == "videoPageXml":
        videoPageXml(urllib.unquote(params['link']))
    if params['action'] == "playVideo":
        playVideo(urllib.unquote(params['link']))
