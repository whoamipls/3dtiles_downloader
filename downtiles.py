import codecs
import getopt
import gzip
import json
import os
import socket
import sys
import traceback
import urllib
from io import StringIO
from urllib import parse, request
from concurrent.futures import ThreadPoolExecutor

SAVE_DIR = 'C:/3dtiles_donwloader'
REMOTE_URL = 'http://211.149.185.229:8080/data/offset_3dtiles/tileset.json'

# REMOTE_URL = 'http://127.0.0.1/develop/tm/code/ABCEarthDemo/examples/assets/temp/bj/tileset.json'

def getContents(n, remoteDir):
    # 下载content url里的东西
    if 'content' in n:
        c = n['content']
        url = c['url'] if 'url' in c else (c['uri'] if 'uri' in c else '')
        if len(url) > 0:
            readContents(remoteDir + "/" + url)
    if 'children' in n:
        children = n['children']
        for i in range(len(children)):
            c = children[i]
            getContents(c, remoteDir)

def readContents(url):
    urlp = urllib.parse.urlparse(url)
    saveFile = SAVE_DIR + urlp.path
    remoteDir, fileName = os.path.split(url)
    # 下载json或b3dm
    r = autoDownLoad(url, saveFile)
    # 如果不是json则退出
    if not url.endswith('.json'):
        return
    # 打开json
    if not r:
        sys.exit(2)
    tileset = None
    try:
        f = codecs.open(saveFile, 'r', 'utf-8')
        s = f.read()
        f.close()
        tileset = json.loads(s)
    except Exception as e:
        print(e)
    #读取json
    getContents(tileset['root'], remoteDir)

def autoDownLoad(url, saveFile):
    try:
        opener = request.build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'),
            ('Accept', 'application/json,*/*;q=0.01,*/*;')]
        request.install_opener(opener)
        savedir, _ = os.path.split(saveFile)
        os.makedirs(savedir, exist_ok=True)

        a, b = request.urlretrieve(url, saveFile)
        # a表示地址， b表示返回头
        keyMap = dict(b)
        if 'Content-Encoding' in keyMap and keyMap['Content-Encoding'] == 'gzip':
            with gzip.open(saveFile, 'rb') as g:
                text = g.read()
                objectFile = open(saveFile, 'rb+')  # 以读写模式打开
                objectFile.seek(0, 0)
                objectFile.write(text)
                objectFile.close()
        return True
    except request.ContentTooShortError:
        print('Network conditions is not good.Reloading.')
        autoDownLoad(url, saveFile)
    except socket.timeout:
        print('fetch ', url, ' exceedTime ')
        try:
            urllib.urlretrieve(url, saveFile)
        except:
            print('reload failed')
    except Exception:
        traceback.print_exc()
    return False

if __name__ == "__main__":
    # 下载目录
    if os.path.isfile(SAVE_DIR):
        print('savedir can not be a file ', SAVE_DIR)
        sys.exit(2)
    os.makedirs(SAVE_DIR, exist_ok=True)
    # 资源目录
    readContents(REMOTE_URL)
    print('done.')
