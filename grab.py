import urllib2,re,time,threading
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
links={}
lock = threading.Lock()
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def write_up(lyric,song):
    global count
    lock.acquire()
    text_file = open(artist+".txt", "a")
    text_file.write(lyric)
    text_file.close()
    print("Grabbed[{}/{}]: {}".format(count,total,song))
    lock.release()
    count+=1


def getSongList(artist_url):
    global hdr,total
    req = urllib2.Request(artist_url,headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page,"lxml")
    soup = soup.find('table',{"class":'tracklist'})
    soup = soup.findAll('a')
    for i,song in enumerate(soup):
        links[i]=[song['title'],song['href']]
    total=len(links)
    print("Obtained the Song list")

def getLyrics(start_index,stop_index):
    global hdr,thread_count
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
        lyric=re.sub(r'''\n{1,40}''',' ',lyric)
        write_up(lyric,song)

def main():
    global artist,count,total
    artist_url = raw_input("Please Enter songLyrics artist url:") #should be of the format http://www.songlyrics.com/xxxxxxx/
    artist=re.findall('\.com\/(.*)\/',artist_url)[0]
    getSongList(artist_url)
    threads,thread_count,count,=[],1,0
    for i in range (9,2,-1):
        if total%i==0:
            thread_count=i
            break
    start,stop=0,total/thread_count


    for i in range(0,thread_count):
        threads.append(threading.Thread(target=getLyrics,args=[start,stop]).start())
        start,stop = stop,stop+total/thread_count
    print("a total of {} thread(s) are created with each handling {} link(s)".format(thread_count,total/thread_count))



if __name__ == "__main__":
    main()
