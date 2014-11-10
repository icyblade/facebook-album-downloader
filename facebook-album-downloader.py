# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import cookielib
import os
import re
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
                        FileTransferSpeed, FormatLabel, Percentage, \
                        ProgressBar, ReverseBar, RotatingMarker, \
                        SimpleProgress, Timer

user_id = '' # USER ID HERE
album_limit = 100
photo_limit = 100 # 100 max
v = 1 # verbose

def createFolder(path):
    if os.path.isdir(path):
        return 'Already exists'
    else:
        os.mkdir(path)
        return 'Created'

def getFileType(url):
    return re.findall('.gif|.jpg|.jpeg|.png', url.lower())[0]

def writePhoto(id, url, path):
    f = urllib.urlretrieve(url, path)
    
def getAlbum(cj, proxy, id):
    url = 'https://graph.facebook.com/%s/albums?limit=%s&fields=id,name' % (id, album_limit)
    opener = urllib2.build_opener(proxy, urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36')
        ]
    try:
        r = opener.open(url)
    except urllib2.HTTPError as e:
        exit()
    json_data = json.loads(r.read())
    arr = []
    for data in json_data['data']:
        arr.append((data['id'], data['name']))
    opener.close()
    return arr
    
def getPhoto(cj, proxy, url, arr=[]):
    opener = urllib2.build_opener(proxy, urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36')
        ]
    r = opener.open(url)
    json_data = json.loads(r.read())
    for data in json_data['data']:
        arr.append((data['id'], data['images'][0]['source']))
    if ('next' in json_data['paging']):
        print '[*] %s found, jumping into %s' % (len(arr), json_data['paging']['next'])
        arr = getPhoto(cj, proxy, json_data['paging']['next'], arr)
    else:
        print'[*] %s found in this album' % len(arr)
        opener.close()
    return arr

def main():
    print '[*] Welcome to Facebook Album Downloader by Icyblade'
    print '[*] Creating download folder...',
    print createFolder('./download')
    cj = cookielib.CookieJar()
    proxy = urllib2.ProxyHandler({'https': '127.0.0.1:8087'})
    print '[*] Getting Album List...',
    album = getAlbum(cj, proxy, user_id)
    print 'Done, %s albums found' % len(album)
    for (album_id, album_name) in album:
        print '[*] Creating album folder "%s"...' % unicode(album_name),
        print createFolder('./download/%s' % trim(album_name))
        print '[*] Getting album "%s" info...' % unicode(album_name)
        photo = getPhoto(cj, proxy, 'https://graph.facebook.com/%s/photos?limit=%s&fields=id,images' % (album_id, photo_limit))
        print '[*] Downloading...'
        i = 0
        pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=len(photo)).start()
        for (photo_id, photo_url) in photo:
            writePhoto(photo_id, photo_url, './download/%s/%s%s' % (album_name, photo_id, getFileType(photo_url)))
            i += 1
            pbar.update(i)
        pbar.finish()

def trim(name):
    return re.sub('[/|\\|:|\*|\?|"|<|>|\|]', '', unicode(name))
    
if __name__ == '__main__':
    main()
    
