import urllib, re, json
import helper

thisChannel = "cbcca"
baseLink = "http://cbc.ca/kids/"

categoryFeedLink = "http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&startIndex=1&endIndex=50&query=HasReleases"

releasesFeedLink = "http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&startIndex=1&endIndex=50&query=categoryIDs|"

ids = [       
#"1328273440", #Kids
#"2214212467",#Kids Holder????????????
#"2222588472",#KidsCBC Interactive
#"2222589425",#Preschool
"2222590020",#TV Shows
"2222613556",#Kids Canada
"2222615963",#Music Videos
]

def mainPage():
    feedLink = categoryFeedLink + "&query=IDs|"+ ','.join(ids)
    showSubMenu(feedLink)

def showCategory(parentID):
    feedLink = categoryFeedLink + "&query=ParentIDs|"+ parentID
    showSubMenu(feedLink)

def showSubMenu(feedLink):
    page = helper.load_page(feedLink)
    data = json.loads(page)
    
    for categoryItem in data['items']:
        action = "showCategory"
        if categoryItem['hasChildren'] == False:
            action = "showVideos"
        print categoryItem['title']
        print categoryItem['ID']
        parameters = {"channel":thisChannel, "action" : action, "link": categoryItem['ID']}
        helper.addDirectoryItem(categoryItem['title'], parameters, categoryItem['thumbnailURL'])
        
    helper.endOfDirectory()
    
def showVideos(id):
    feedLink = releasesFeedLink+id
    page = helper.load_page(feedLink)
    data = json.loads(page)
    for releaseItem in data['items']:
        length = str(int(releaseItem['length'])/1000/60)
        parameters = {"channel":thisChannel, "action" : "playVideo", "link": releaseItem['URL']}
        helper.addDirectoryItem(releaseItem['title'], parameters, releaseItem['thumbnailURL'],False,duration=length)
    
    helper.endOfDirectory()

def playVideo(link):
    streamUrl = helper.load_page(link,getRedirect=True)
    
    if not streamUrl == link:
        streamUrl = streamUrl.replace("<break>"," playpath=MP4:")
    else:
        streamPage = helper.load_page(link)
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
    if params['action'] == "showCategory":
        showCategory(params['link'])
    if params['action'] == "showVideos":
        showVideos(params['link'])
    if params['action'] == "playVideo":
        playVideo(urllib.unquote(params['link']))