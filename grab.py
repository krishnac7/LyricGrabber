import urllib2,re,time,threading
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
artist_url={}
lock = threading.Lock()
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

global total,count
threads,total,count = [],0,1

def getArtistUrls():
    artist_url,url={},{}
    if len(sys.argv)<2:
        url=raw_input("\nPlease enter Songlyric artist urls seperated by space: ").split()
    else:
        url=sys.argv[1:]
    for x in url:
        try:
         artist_url[re.findall('\.com\/(.*)\/',x)[0]]=x
        except:
            print("{} is not a valid url\n".format(x))
    if len(artist_url)==0:
        print("Nothing to Grab \nExiting program..")
        sys.exit(0)
    for artist,url in artist_url.items():
        threads.append(threading.Thread(target=getSongList,args=[artist,url]).start())


def write_up(artist,lyric,song):
    global total,count
    lock.acquire()
    text_file = open(artist+".txt", "a")
    text_file.write(lyric)
    text_file.close()
    print("Grabbed[{}/{}] : {}\n".format(count,total,song))
    lock.release()
    count+=1


def getSongList(artist,artist_url):
    global hdr,total
    links={}
    req = urllib2.Request(artist_url,headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page,"lxml")
    soup = soup.find('table',{"class":'tracklist'})
    soup = soup.findAll('a')
    for i,song in enumerate(soup):
        links[i]=[song['title'],song['href']]
    numlinks=len(links)
    total+=numlinks
    print("Obtained the Song list of {}\n".format(artist[:-7]))
    thread_count=1
    for i in range (9,2,-1):
        if numlinks%i==0:
            thread_count=i
            break
    start,stop=0,numlinks/thread_count

    for i in range(0,thread_count):
        threads.append(threading.Thread(target=getLyrics,args=[artist,start,stop,links]).start())
        start,stop = stop,stop+numlinks/thread_count

def getLyrics(artist,start_index,stop_index,links):
    global hdr
    shr={}
    for i in range(start_index,stop_index):
        shr[links[i][0]]=links[i][1]
    for song, link in shr.items():
        try:
            req = urllib2.Request(link,headers=hdr)
            page = urllib2.urlopen(req)
        except Exception as e:
            print(e)
            continue
        soup = BeautifulSoup(page,"lxml")
        lyric=str(soup.find('p',{'id':'songLyricsDiv'}))
        lyric=re.sub(r'''<p.*">|<br/>|</p>|(\(.*\))''','',lyric)

        # lyric=re.sub(r'''\n{1,40}''',' ',lyric)

        # Uncomment the above line and
        # comment below line if you are using this to obtain data for your markov chain

        lyric="\n"+song+":\n"+lyric
        write_up(artist,lyric,song)

def main():
        getArtistUrls()


if __name__ == "__main__":
    main()
