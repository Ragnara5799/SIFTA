__author__ = 'niklas'
from lxml import html
import requests
import random
import os
import threading
import time
from Queue import Queue
from googleplay import GooglePlayAPI

startappID = "tamigo.android.activities"
#startappID = "com.facebook.katana"
baseURL = "https://play.google.com/store/apps/details?id="
appQueue = Queue()
downloaded = set()
downloadQueue = Queue()
errors = Queue()


class CrawlerThread(threading.Thread):
    def __init__(self, destfolder, firstApp):
        super(CrawlerThread, self).__init__()
        self.destfolder = destfolder
        self.firstApp = firstApp
        self.daemon = True
        self.running = True
        self.stopped = False

    def run(self):
        lst = Queue()
        item = appQueue.get()
        lst.put(item)
        appQueue.put(item)
        while not lst.empty() and self.running:
            #print appQueue.qsize()
            if appQueue.qsize() > 100:
                time.sleep(1)
                print "waiting... queue size: " + str(appQueue.qsize())
            else:
                current = lst.get()
                page = requests.get(baseURL+current)
                tree = html.fromstring(page.text)
                related = tree.xpath("//div[@class='card-content id-track-click id-track-impression']/a[@class='card-click-target']/@href")
                for e in related:
                    id = e.split("id=")[1]
                    lst.put(id)
                    if id not in downloaded:
                        appQueue.put(id)
                        #print "added: " + id + " to queue"
                        downloaded.add(id)
                        downloadQueue.put(id)
        self.stopped = True
    def stop(self):
        self.running = False

class DownloadThread(threading.Thread):
    def __init__(self, queue, destfolder, playapi):
        super(DownloadThread, self).__init__()
        self.queue = queue
        self.destfolder = destfolder
        self.daemon = True
        self.playapi = playapi
        self.running = True
        self.stopped = False

    def run(self):
        while self.running:
            if self.queue.empty():
                print "waiting...."
                time.sleep(5)
            else:
                id = self.queue.get()
                try:
                    print "[%s] downloading: %s" % (self.ident, id)
                    details = self.playapi.details(id)
                    #print details
                    version = details.docV2.details.appDetails.versionCode
                    print id + " " + str(version)
                    apk = self.playapi.download(id, version)
                    print "finished dowloading " + id
                    f = open("../playapks/"+id+".apk", 'w')
                    f.write(apk)
                    f.close()
                    print "written " + id + " to file"
                except Exception, e:
                    print "Error on downloading :" + id
                    print e
                    errors.put(id)
                    continue
                self.queue.task_done
        self.stopped = True

    def stop(self):
        self.running = False

class FileThread(threading.Thread):
    def __init__(self):
        super(FileThread, self).__init__()
        self.running = True
        self.stopped = False

    def run(self):
        while self.running and not self.stopped:
            while not errors.empty():
                error = errors.get()
                f = open("errors.txt", "a")
                f.write(error + "\n")
                f.close()

            while not downloadQueue.empty():
                download = downloadQueue.get()
                f = open("downloaded.txt", "a")
                f.write(download + "\n")
                f.close()
            time.sleep(1)
        self.stopped = True

    def stop(self):
        self.running = False

def checkExisting():
    queueFile = open("queue.txt", "r")
    queueLines = queueFile.readlines()
    for queue in queueLines:
        appQueue.put(queue[:-1])
    downloadFile = open("downloaded.txt", "r")
    downloadLines = downloadFile.readlines()
    for download in downloadLines:
        downloaded.add(download[:-1])
    errorFile = open("errors.txt", "r")
    errorLines = errorFile.readlines()
    for error in errorLines:
        downloaded.add(error[:-1])

def downloadAPKs(start):
    crawler = CrawlerThread("../playapks/", startappID)
    crawler.start()
    time.sleep(1)

    threads = []

    playapi = GooglePlayAPI()
    playapi.login("androidhaxor42@gmail.com", "niklashaxor42")


    for i in range(10):
        t = DownloadThread(appQueue, "../playapks/", playapi)
        t.start()
        threads.append(t)

    filewriter = FileThread()
    filewriter.start()

    done = False
    #OMG DON'T DIE!
    while not done:
        test = raw_input(">")
        if test == "exit":
            print "Killing threads..."
            for thread in threads:
                thread.stop()
            crawler.stop()
            filewriter.stop()
            while len([t for t in threads if t.stopped == True]):
                time.sleep(1)
                print "Waiting for threads to finish..."
            print "Exiting..."
            done = True


    if os.path.exists("queue.txt"):
        os.remove("queue.txt")

    queueFile = open("queue.txt", 'w')

    for a in list(appQueue.queue):
        queueFile.write(a+"\n")

    queueFile.close()


checkExisting()
downloadAPKs(startappID)