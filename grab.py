from __future__ import print_function
import re,time,threading,os.path,sys
import urllib.request as urllib2
from bs4 import BeautifulSoup
from math import sqrt,floor
start_time = time.time()
artist_url={}
lock = threading.Lock()
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

global total,count,failed
threads,total,count,failed = [],0,1,0

def getArtistUrls():
    artist_url,url={},{}
    if len(sys.argv)<2:
        url=input("\nPlease enter Songlyric artist urls seperated by space: ").split()
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

def getSongList(artist,artist_url):
    if os.path.exists(str(artist)+'.txt'):
        os.remove(str(artist)+'.txt')
        print("Removed old {} lyrics file".format(artist))
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
    print("Obtained the Song list of {}".format(artist[:-7]))
    root = int(floor(sqrt(numlinks)))
    thread_count=root
    start,stop=0,root
    for i in range(0,thread_count):
        threads.append(threading.Thread(target=getLyrics,args=[artist,start,stop,links]).start())
        start,stop = stop,stop+root
    if root**2!=numlinks:
        threads.append(threading.Thread(target=getLyrics,args=[artist,start,start+(numlinks-start),links]).start())
        print("\n{} threads are created for {} with each handling {} song(s) except the last one which is handeling {} song(s)\n".format(root+1,artist,root,numlinks-root**2))
    else:
        print("\n{} threads are created for {} with each handling {} song(s)\n".format(root,artist,root))

def getLyrics(artist,start_index,stop_index,links):
    global hdr,failed
    shr={}
    for i in range(start_index,stop_index):
        shr[links[i][0]]=links[i][1]
    for song, link in shr.items():
        try:
            req = urllib2.Request(link,headers=hdr)
            page = urllib2.urlopen(req)
        except Exception as e:
            print(e)
            failed+=1
            continue
        soup = BeautifulSoup(page,"lxml")
        lyric=str(soup.find('p',{'id':'songLyricsDiv'}))
        lyric=re.sub(r'''<p.*">|<br/>|</p>|(\(.*\))''','',lyric)

        #lyric=re.sub(r'''\n{1,40}''',' ',lyric)

        # Uncomment the above line and
        # comment below line if you are using this to obtain data for your markov chain

        lyric="\n"+song+":\n"+lyric
        write_up(artist,lyric,song)

def write_up(artist,lyric,song):
    global total,count,failed
    lock.acquire()
    try:
        text_file = open(artist+".txt", "a")
    except e:
        print("Please re check the url and enter only artist url")
    text_file.write(lyric)
    text_file.close()
    print("Grabbed[{}/{}] : {}".format(count,total,song))
    lock.release()
    if count==total-failed:
        print("\nGrabbed {} song lyrics in: {:.2f} Seconds and {} failed".format(total,time.time() - start_time,failed))
    count+=1




def main():
        getArtistUrls()


if __name__ == "__main__":
    main()
