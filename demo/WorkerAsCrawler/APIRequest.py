# coding:utf-8
'''
__author__ = "Liu Kun"
__start_date__ = "2018-03-03"
'''
__python__ = 3.6
import urllib
import urllib.request
import json

KEY_FILE_PATH = "KEYS"

CURRENT_KEY = ""
API_LIST = []
def get_available_key():
    global CURRENT_KEY, API_LIST
    if not CURRENT_KEY:
        if not API_LIST:
            API_LIST = open(KEY_FILE_PATH).readlines()
        CURRENT_KEY = API_LIST.pop()
    return CURRENT_KEY.strip()

def request_json_url(url):
    # user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    # headers = {
    #     'Connection': 'Keep-Alive',
    #     'Accept': 'text/html, application/xhtml+xml, */*',
    #     'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    # }
    try:
        content = urllib.request.urlopen(url, timeout=10).read().decode("utf-8")
        json_data = json.loads(content)
        return json_data
    except Exception as e:
        print("Exception happend whhen request %s"%url)
        print(e)
        with open("fail_url.txt", "a+") as fw:
            fw.write(url+"\n")
        global CURRENT_KEY
        CURRENT_KEY = ""
        return {}

class UserAPI:
    def __init__(self, user_id):
        self.api_key = get_available_key()
        self.user_id = user_id
        self.function_url = "http://ws.audioscrobbler.com/2.0/?method={method}&user={user_id}&api_key={key}&format=json"

    def get_function_url(self, func):
        return self.function_url.format(
            method="user."+func, key=self.api_key, user_id=self.user_id
        )

    def get_info(self):
        #获取用户信息，重要
        url = self.function_url.format(
            method="user.getInfo", key=self.api_key, user_id=self.user_id
        )
        resp_json = request_json_url(url)
        if not resp_json:
            self.api_key = get_available_key()
            url = self.function_url.format(
                method="user.getInfo", key=self.api_key, user_id=self.user_id
            )
            resp_json = request_json_url(url)
        return resp_json 
    
    def get_friends(self):
        #获取朋友用户，重要
        url = self.function_url.format(
            method="user.getfriends", key=self.api_key, user_id=self.user_id
        )+"&limit=200"
        resp_json = request_json_url(url)
        if not resp_json:
            self.api_key = get_available_key()
            url = self.function_url.format(
                method="user.getfriends", key=self.api_key, user_id=self.user_id
            )+"&limit=200"
            resp_json = request_json_url(url)
        return resp_json 
    
    def get_loved_tracks(self):
        #获取喜爱的音乐，重要(数量为最近的50个)
        url = self.function_url.format(
            method="user.getlovedtracks", key=self.api_key, user_id=self.user_id
        )
        return request_json_url(url)       

    # def get_personal_tags(self):
    #     url = self.get_function_url(func="getpersonaltags")
    #     return request_json_url(url)
    
    def getTopTracks(self, request_pages=1):
        # 获取所有播放过的歌曲以及播放次数，需要翻页获取所有记录
        url = self.get_function_url("gettoptracks")+"&limit=200"+"&format=json"
        front_data = request_json_url(url)
        page_number = int(front_data["toptracks"]["@attr"]["totalPages"])
        if request_pages == 0:
            request_pages = page_number
        else:
            request_pages = min(int(page_number), request_pages)
        for page in range(2, 1+request_pages):
            next_page_url = url+"&page=%d"%page
            new_data = request_json_url(next_page_url)
            front_data["toptracks"]["track"].append(new_data["toptracks"]["track"])
        return front_data

    def getRecentTracks(self, request_pages=1):
        #获取播放过的音乐，需要靠翻页来得到所有歌曲
        url = self.get_function_url("getrecenttracks")+"&limit=200"
        front_data = request_json_url(url)
        page_number = int(front_data["recenttracks"]["@attr"]["totalPages"])
        if request_pages == 0:
            request_pages = page_number
        else:
            request_pages = min(page_number, request_pages)
        for page in range(2, 1+request_pages):
            next_page_url = url+"&page=%d"%page
            new_data = request_json_url(next_page_url)
            front_data["recenttracks"]["track"].append(new_data["recenttracks"]["track"])
        return front_data

    def getTopAlbums(self):
        #获取听过的专辑和播放次数
        url = self.get_function_url("gettopalbums")
        return request_json_url(url)

    def getTopArtists(self):
        #获取播放最多量最多的歌曲的艺人
        url = self.get_function_url("gettopartists")
        return request_json_url(url)

    def getTopTags(self):
        #获取用户给音乐打过的标签
        url = self.get_function_url("gettoptags")
        return request_json_url(url)

    def getWeeklyTrackChart(self):
        #获取一周播放音乐列表
        url = self.get_function_url("getweeklytrackchart")
        return request_json_url(url)

class TrackAPI:
    def __init__(self, track_name="", artist="", mbid=""):
        self.track_name = track_name
        self.artist = artist
        self.api_key = get_available_key()
        self.function_url = "http://ws.audioscrobbler.com/2.0/?method=track.{method}&artist={artist_name}&track={track_name}&api_key={key}&format=json"
        self.mbid = mbid

    def get_function_url(self, func):
        return self.function_url.format(
            method=func, key=self.api_key, track_name=self.track_name, artist_name=self.artist
        )

    def get_info(self):
        url = self.get_function_url("getinfo")
        return request_json_url(url)

    def get_info_by_mbid(self):
        self.api_key = get_available_key()
        url = "http://ws.audioscrobbler.com/2.0/?method=track.getinfo&mbid={mbid}&api_key={key}&format=json".format(mbid=self.mbid, key=self.api_key)
        return request_json_url(url)

class AlbumAPI:
    def __init__(self, artist_name, album_name):
        self.artist_name = artist_name
        self.album_name = album_name
        self.api_key = get_available_key()
        self.function_url = "http://ws.audioscrobbler.com/2.0/?method=album.{method}&artist={artist_name}&album={album_name}&api_key={key}&format=json"

    def get_function_url(self, func):
        return self.function_url.format(
            method=func, key=self.api_key, album_name=self.album_name, artist_name=self.artist_name
        )

    def get_info(self):
        url = self.get_function_url("getinfo")
        return request_json_url(url)

class TagAPI:
    def __init__(self, tag):
        self.tag = tag
        self.api_key = get_available_key()
    
    def get_info(self):
        url = "http://ws.audioscrobbler.com/2.0/?method=tag.getinfo&tag=%s&api_key=%s&format=json"%(self.tag, self.api_key)
        return request_json_url(url)

class ArtistAPI:
    def __init__(self, artist_name):
        self.artist_name = artist_name
        self.api_key = get_available_key()
    
    def get_info(self):
        url = "http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=%s&api_key=%s&format=json"%(self.artist_name, self.api_key)
        return request_json_url(url)       

#--------------------test---------------------
def main():
    #u1 = UserAPI("hutazone")
    import pprint
    #pprint.pprint(u1.getTopTracks(request_pages=3))
    # pprint.pprint(u1.get_loved_tracks())
    #t1 = TrackAPI("cOOl hOT sWeEt lOvE", "Red Velvet")
    #pprint.pprint(t1.get_info())
    #album1 = AlbumAPI("Ringo Starr","Ringo")
    #pprint.pprint(album1.get_info())
    # artist_1 = ArtistAPI("Ringo Starr")
    # pprint.pprint(artist_1.get_info())
    # tag1 = TagAPI("k-pop")
    # pprint.pprint(tag1.get_info())
    track1 = TrackAPI(mbid="000002e1-d595-442e-97a6-2e2f4c85cef7")
    print(track1.get_info_by_mid())

if __name__ == '__main__':
    main()

