#!/usr/bin/python
import os,httplib,re,time
from sys import stderr
from urllib import urlretrieve as wget
pjoin = os.path.join
basedir = os.path.dirname(os.path.abspath(__file__))
basedir = pjoin(basedir, "data")

WAIT=0.025 # the time to wait between fetching pages (in seconds)

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
    

def main(justTitles=False):
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