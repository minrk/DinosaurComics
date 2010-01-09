#!/usr/bin/python
# try:
from __future__ import with_statement # for python2.5
# except:
    # pass
import os,httplib,re,time
from sys import stderr
from urllib import FancyURLopener

from threading import Thread, RLock

pjoin = os.path.join

basedir = os.path.dirname(os.path.abspath(__file__))
basedir = pjoin(basedir, "data")

WAIT=0.025 # the time to wait between fetching pages (in seconds)
numthreads=16

if not os.path.isdir(basedir):
    os.mkdir(basedir)
if not os.path.isfile(pjoin(basedir, "titles.txt")):
    f = open(pjoin(basedir, "titles.txt"),'w')
    f.close()

def unescape(s):
    m = 1
    while m:
        m = re.search("\&\#\d*?;", s)
        if m is None:
            continue
        match = m.group()
        n = int(m.group()[2:-1])
        s = s.replace(match, chr(n))
    s = s.replace("&quot;",'"')
        
    return s

class FetchThread(Thread):
    def __init__(self, master):
        Thread.__init__(self)
        self.master=master
        self.ht = httplib.HTTPConnection('www.qwantz.com')
        self.ht.connect()
        self.getter = FancyURLopener()
    
    def run(self):
        notdone = True
        while notdone:
            
            r = self.fetch()
            # if False:
            with self.master.fourLock:
                if r != 200 and r is not None:
                    self.master.fourofours += 1
                else:
                    self.master.fourofours =0
                notdone = self.master.fourofours < 7
            if r == 200:
                with self.master.writeLock:
                    self.master.writeTitles()
            
    def fetch(self):
        with self.master.numLock:
            n = self.master.toget.pop(0)
        justTitle=False
        if os.path.isfile(pjoin(basedir,"dinocomics%06i.png"%(n))):
            if n in self.master.titles.iterkeys():
                return None
            else:
                justTitle=True
        
        # print >> stderr,n
        
        ht = self.ht
        ht.request("GET","/index.php?comic=%i"%n)
        # time.sleep(1)
        # time.sleep(1)ma
        try:
            r = ht.getresponse()
        except: # new connection
            ht = httplib.HTTPConnection('www.qwantz.com')
            ht.connect()
            self.ht = ht
            time.sleep(1)
            # print dir(ht)
            # try:
            r = ht.getresponse()
            # except Exception, e:
                # raise e
        if r.status != 200:
            if r.status in (404, 302):
                print >> stderr, n, "No Comic"
            else:
                print >> stderr,  n, "FAILED: %i"%r.status
            ht = httplib.HTTPConnection('www.qwantz.com')
            ht.connect()
            self.ht = ht
            return r.status
        s = r.read()
        m = re.search('\<img *src *= *"http://www.qwantz.com/comics.*?\>', s,re.S)
        if m is None:
            print >> stderr, n,"no match!1"
            return r.status
        img = m.group()
        m = re.search('src *= *".*?"', img,re.S)
        if m is None:
            print >> stderr, n,"no match!2"
            return r.status
        href = re.search('".*?"',m.group(),re.S).group()[1:-1]
        m = re.search('title *= *".*?"', img,re.S)
        if m is None:
            print >> stderr, n,"no match!3"
            return r.status
        title = re.search('".*"',m.group(),re.S).group()[1:-1].strip()
        
        title = unescape(title)
        title = title.replace("\r\n","\\n")
        title = title.replace("\n","\\n")
        while True:
            prevtitle = title
            title = title.replace("\\n\\n","\\n")
            if prevtitle == title:
                break
        # print repr(title)
        # return
        # self.master.titleLock.acquire()
        with self.master.titleLock:
            self.master.titles[n] = title
        # self.master.titleLock.release()
        print >> stderr, n,title
        if not justTitle:
            self.getter.retrieve(href,"%s/dinocomics%06i.png"%(basedir,n))
        return r.status


class FetchMaster(object):
    def __init__(self,nthreads=1,justTitles=False):
        """docstring for __init__"""
        titles = {}
        self.nthreads=nthreads
        self.done=False
        self.fourofours=0
        self.justTitles=justTitles
        self.toget = range(1,3000)
        self.writing=False
        try:
            f = open(pjoin(basedir,'titles.txt'),'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                ns,title = line.split(' ',1)
                titles[int(ns)] = title[:-1]
        except Exception, e:
            log.error(e.message)
            pass
            
        self.titles = titles
        self.threads = [FetchThread(self) for n in xrange(self.nthreads)]
        self.titleLock = RLock()
        self.numLock = RLock()
        self.writeLock = RLock()
        self.fourLock = RLock()
    
    def fetch(self, justTitles=False):
        # while self.fourofours < 7:
        statuses = [ t.start() for t in self.threads ]
        for t in self.threads:
            while t.isAlive():
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    pass
            # print >>stderr, "Thread", t.ident, "done"
            # if 200 in statuses:
            #     self.fourofours=0
            # else:
            #     self.fourofours += len(self.threads)
        print >>stderr, "Done Fetching up to %i"%max(self.titles.iterkeys())
    
    def writeTitles(self):
        f = open(pjoin(basedir,'titles.txt'),'w')
        for k in sorted(self.titles.keys()):
             f.write("%i %s\n"%(k,self.titles[k]))
        f.close()
            
            
        
    

def main(justTitles=False):
    master = FetchMaster(numthreads)
    master.fetch()

def oldmain(justTitles=False):
    ht = httplib.HTTPConnection('www.qwantz.com')
    ht.connect()
    titles = {}
    try:
        f = open(pjoin(basedir,'titles.txt'),'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            ns,title = line.split(' ',1)
            titles[int(ns)] = title[:-1]
    except Exception, e:
        log.error(e.message)
        pass
    # nmin = max(533, max(titles.keys()+[0])+1)
    nlist = xrange(1,3000)
    # for n in titles.keys():
        # nlist.remove(n)
    # nmin = 1
    # print nmin
    # return
    fourofours = 0
    try:
      for n in nlist:
        # print n
        # if justTitles or not os.path.isfile("dinocomics%06i.png"%(n)):
        if not os.path.isfile(pjoin(basedir,"dinocomics%06i.png"%(n))):
            print >> stderr,n
            ht.request("GET","/index.php?comic=%i"%n)
            time.sleep(WAIT)
            # time.sleep(1)ma
            try:
                r = ht.getresponse()
            except:
                ht = httplib.HTTPConnection('www.qwantz.com')
                ht.connect()
                time.sleep(.5)
                r = ht.getresponse()
            if r.status != 200:
                if r.status == 302:
                    fourofours += 1
                if fourofours > 6:
                    print >> stderr, "got %i 404/302s, probably the end"%fourofours
                    break
                print >> stderr,"Request Failed! %s"%r.status
                ht = httplib.HTTPConnection('www.qwantz.com')
                ht.connect()
                continue
            else: # reset checks for the end
                fourofours = 0
            s = r.read()
            # time.sleep(2)
            # s2 = r.read()
            # print "s2",s2
            m = re.search('\<img *src *= *"http://www.qwantz.com/comics.*?\>', s,re.S)
            if m is None:
                print >> stderr, "no match!1"
                continue
            img = m.group()
            m = re.search('src *= *".*?"', img,re.S)
            # print m
            if m is None:
                print >> stderr, "no match!2"
                continue
            href = re.search('".*?"',m.group(),re.S).group()[1:-1]
            m = re.search('title *= *".*?"', img,re.S)
            if m is None:
                print >> stderr, "no match!3"
                continue
            title = re.search('".*"',m.group(),re.S).group()[1:-1].strip()
            #.replace("\n","\\n")
            # print repr(title)
            title = unescape(title)
            title = title.replace("\r\n","\\n")
            title = title.replace("\n","\\n")
            for i in xrange(4):
                title = title.replace("\\n\\n","\\n")
            # print repr(title)
            # return
            titles[n] = title
            # print >> stderr, href
            print >> stderr, title
            if not justTitles:
                wget(href,"%s/dinocomics%06i.png"%(basedir,n))
            f = open(pjoin(basedir,'titles.txt'),'w')
            for k in sorted(titles.keys()):
                 f.write("%i %s\n"%(k,titles[k]))
            f.close()
        
                
    except KeyboardInterrupt:
        pass
        # print "A"*24, e
    f = open(pjoin(basedir,'titles.txt'),'w')
    for k in sorted(titles.keys()):
        f.write("%i %s\n"%(k,titles[k]))
    f.close()
    print >> stderr, "Done!"
    
if __name__ == '__main__':
    main(False)