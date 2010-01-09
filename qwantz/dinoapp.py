#!/usr/bin/env python

import Image, os

import _imaging#,PIL # for py2app
from pilutil import fromimage, toimage
from signal import SIGINT, SIGTERM
from random import randint
# from fetch import main as fetch
import fetchthread as fetch
# import fetch
# import Tkinter
import wx,time,threading
pjoin = os.path.join
basedir = os.path.dirname(os.path.abspath(__file__))
basedir = pjoin(basedir, "data")
# print basedir
shape = (500,735,3)
panels = [None,
 (slice(0,242),slice(0,244)),
 (slice(0,242),slice(244,374)),
 (slice(0,242),slice(374,None)),
 (slice(242,None),slice(0,195)),
 (slice(242,None),slice(195,493)),
 (slice(242,None),slice(493,None))]

if  os.path.isfile(pjoin(basedir,"titles.txt")):
    titles = {}
    f = open(pjoin(basedir,'titles.txt'),'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        ns,title = line.split(' ',1)
        titles[int(ns)] = title[:-1].replace("\\n","\n")

    nlist = titles.keys()
    J = len(nlist)-1
else:
    titles = {}
    nlist = titles.keys()
    J = 0

def piltowx(pil,alpha=True):
    """Convert PIL Image to wx.Image."""
    if alpha:
        image = apply( wx.EmptyImage, pil.size )
        image.SetData( pil.convert( "RGB").tostring() )
        image.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
    else:
        image = wx.EmptyImage(pil.size[0], pil.size[1])
        new_image = pil.convert('RGB')
        data = new_image.tostring()
        image.SetData(data)
    return image

def wxtopil(image):
    """Convert wx.Image to PIL Image."""
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.fromstring(image.GetData())
    return pil

def crop(im,slices):
    return toimage(fromimage(im)[slices])

def copyPanel(ima,imb,p):
    a = fromimage(ima)
    b = fromimage(imb)
    try:
        a[panels[p]] = b[panels[p]]
    except:
        # print a.shape,ima.size,b.shape,imb.size
        ima.show()
        imb.show()
    return toimage(a)

def load(n=None):
    try:
        if not n:
            n = nlist[randint(0,J)]
        im = Image.open(pjoin(basedir, "dinocomics%06i.png"%n))
        wxtest = piltowx(im) # error Interlaced PNGs
        # print n,fromimage(im).shape
        # assert(fromimage(im).shape == (500,735,3)), "Not the right shape"
        # print im.size
        while im.size != (735,500): # ignore wrong sized images (guest comics)
            # print im.size
            # copyPanel(load(1),im,2)
            n = nlist[randint(0,J)]
            im = Image.open(pjoin(basedir, "dinocomics%06i.png"%n))
            wxtest = piltowx(im)
        return im
        # except AssertionError
    except Exception, e:
        print "Load Error: %i"%n,e
        # import sys
        # sys.exit()
        # if n < J:
        n = n%nlist[-1]
        time.sleep(1)
        return load(n+1)
        

def randomizePanel(im,ps=range(1,7),show=True):
    if isinstance(ps,int):
        ps = [ps]
    for p in ps:
        im = copyPanel(im,load(),p)
    if show:
        im.show()
    return im

def randomDino():
    # ns = [nlist[i] for i in map(randint, [0]*7,[J]*7) ]
    # print ns
    im = load()
    for i in range(2,7):
        im = randomizePanel(im, i,False)
    # print titles[nlist[randint(0,J)]]
    im.show()
    return im
# ID_BUTTON1=110
ID_EXIT=200
class DinoComics(wx.App):
    def OnInit(self):
        self.fetcher = None
        frame = wx.Frame(None,-1,"Fetching Comics")
        self.fetchFrame = frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.fetchLabel = wx.StaticText(frame,label="0 Comics",size=(24*8,24),style=wx.TE_READONLY)
        stop  = wx.Button(frame,975,"Stop Fetching")
        wx.EVT_BUTTON(frame, 975, self.stopFetching)
        sizer.Add(self.fetchLabel,wx.EXPAND)
        sizer.Add(stop,wx.EXPAND)
        # label.SetVa
        
        frame.SetSizer(sizer)
        sizer.Fit(frame)
        frame.Show(0)
        # self.root = parent
        # self.frame = Tkinter.Frame(parent)
        self.frame = wx.Frame(None,-1,"Dinosaur Comics")
        self.frame.Show(True)
        # self.frame.SetTopWindow(True)
        self.lbox = wx.BoxSizer(wx.VERTICAL)
        self.mbox = wx.BoxSizer(wx.VERTICAL)
        self.sbox = wx.BoxSizer(wx.VERTICAL)
        # self.buttons = []
        # self.locks = [False]*6
        l = wx.StaticText(self.frame,0,"Context")
        self.sbox.Add(l,1,wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
        for n in range(1,7):
            b = wx.Button(self.frame,n+200,"Panel %i"%n)
            wx.EVT_BUTTON(self.frame, n+200, self.syncPanel)
            self.sbox.Add(b,1,wx.EXPAND)
            b = wx.Button(self.frame,n+100,"Last %i"%n)
            wx.EVT_BUTTON(self.frame, n+100, self.prevPanel)
            self.lbox.Add(b,1,wx.EXPAND)
            b = wx.Button(self.frame,n,"New %i"%n)
            wx.EVT_BUTTON(self.frame, n, self.nextPanel)
            self.mbox.Add(b,1,wx.EXPAND)
            # self.buttons.append(b)
        
        b = wx.Button(self.frame,200,"Title")
        wx.EVT_BUTTON(self.frame, 200, self.syncPanel)
        self.sbox.Add(b,1,wx.EXPAND)
        b = wx.Button(self.frame,107,"Last Title")
        wx.EVT_BUTTON(self.frame, 107, self.prevTitle)
        self.lbox.Add(b,1,wx.EXPAND)
        b = wx.Button(self.frame,7,"New Title")
        wx.EVT_BUTTON(self.frame, 7, self.nextTitle)
        self.mbox.Add(b,1,wx.EXPAND)
        
        b = wx.Button(self.frame,808,"Dada")
        wx.EVT_BUTTON(self.frame, 808, self.randomDada)
        self.lbox.Add(b,1,wx.EXPAND)
        b = wx.Button(self.frame,8,"Random Comic")
        wx.EVT_BUTTON(self.frame, 8, self.randomComic)
        self.mbox.Add(b,1,wx.EXPAND)
        
        b = wx.Button(self.frame,9,"Fetch Comics")
        wx.EVT_BUTTON(self.frame, 9, self.fetch)
        self.mbox.Add(b,1,wx.EXPAND)
        self.exit = wx.Button(self.frame,888, "Exit")
        wx.EVT_BUTTON(self.frame,888, self.OnExit)
        self.lbox.Add(self.exit,1,wx.EXPAND)
        self.save = wx.Button(self.frame,999, "Save")
        wx.EVT_BUTTON(self.frame,999, self.OnSave)
        self.sbox.Add(self.save,1,wx.EXPAND)
        
        
        self.rbox = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.TextCtrl(self.frame, style=wx.TE_READONLY|wx.TE_MULTILINE)
        self.imPanel = wx.Panel(self.frame,size=(735,500))
        self.rbox.Add(self.imPanel,1,wx.EXPAND)
        self.rbox.Add(self.title,0,wx.EXPAND)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.lbox,0,wx.EXPAND)
        self.hbox.Add(self.mbox,0,wx.EXPAND)
        self.hbox.Add(self.rbox,1,wx.EXPAND)
        self.hbox.Add(self.sbox,0,wx.EXPAND)
        self.frame.SetSizer(self.hbox)
        self.hbox.Fit(self.frame)
        self.frame.Show(1)
        self.dirname = os.path.join(os.path.expanduser("~"),"Desktop")
        if not os.path.isdir(self.dirname):
            self.dirname = os.path.expanduser("~")
            if not os.path.isdir(self.dirname):
                self.dirname = ""
        
        if len(titles) < 1:
            self.title.SetValue("Fetching Some Comics...")
            self.fetch()
            global J
            while J < 1:
                time.sleep(1)
        
        self.image = load()
        
        x,y = self.image.size
        self.wximage = piltowx(self.image)
        self.imPanel.OnPaint = lambda evt: wx.PaintDC(self.imPanel).DrawBitmap(self.wximage.ConvertToBitmap(),0,0)
        self.imPanel.Bind(wx.EVT_PAINT, self.imPanel.OnPaint)
        self.imPanel.Refresh(True)
        
        self.panels = [[],[],[],[],[],[],[]]
        self.extend()
        self.active = [-1]*7
        for i in range(1,7):
            self.nextPanel(i)
        self.nextTitle(None)
        self.title.SetValue(titles[self.panels[0][0]])
        
        # self.newTitle(1)
        return True
    
    def extend(self):
        for i in range(4):
            for p in self.panels:
                p.append(nlist[randint(0,J)])
    
    def OnExit(self, evt=None):
        try:
            self.stopFetching(None)
            wx.CallAfter(self.fetchFrame.Destroy)
        except:
            pass
        try:
            wx.CallAfter(self.frame.Destroy)
        except:
            pass
        self.Exit()
    
    def syncPanel(self, evt):
        if isinstance(evt, int):
            p = evt
        else:
            p = evt.Id - 200
        n = self.panels[p][self.active[p]]
        self.image = load(self.panels[p][self.active[p]])
        for p in range(7):
            i = self.active[p]
            if self.panels[p][i] != n:
                self.panels[p].insert(i+1,n)
                self.active[p] = i+1
        
        self.wximage = piltowx(self.image)
        self.imPanel.Refresh(True)
        self.title.SetValue(titles[n])
        # print len(titles),J
        
            
    def nextPanel(self, evt):
        if isinstance(evt, int):
            n = evt
        else:
            n = evt.Id
        if self.active[n] == len(self.panels[n])-1:
            self.extend()
        self.active[n] += 1
        self.image = copyPanel(self.image,load(self.panels[n][self.active[n]]),n)
        self.wximage = piltowx(self.image)
        self.imPanel.Refresh(True)
    
    def prevPanel(self, evt):
        if isinstance(evt, int):
            n = evt
        else:
            n = evt.Id - 100
        if self.active[n] == 0:
            return
        self.active[n] -= 1
        self.image = copyPanel(self.image,load(self.panels[n][self.active[n]]),n)
        self.wximage = piltowx(self.image)
        self.imPanel.Refresh(True)
        
    
    def nextTitle(self, evt):
        if self.active[0] == len(self.panels[0])-1:
            return
        self.active[0] += 1
        self.title.SetValue(titles[self.panels[0][self.active[0]]])
    
    def prevTitle(self, evt):
        if self.active[0] == 0:
            return
        self.active[0] -= 1
        self.title.SetValue(titles[self.panels[0][self.active[0]]])
    
    def randomDada(self, evt):
        map(self.nextPanel, range(1,7))
        self.nextTitle(None)
    
    def randomComic(self, evt):
        n = nlist[randint(0,J)]
        self.image = load(n)
        self.wximage = piltowx(self.image)
        self.imPanel.Refresh(True)
        self.title.SetValue(titles[n])
    
    
    def stopFetching(self,evt):
        if self.fetcher is not None:
            if self.fetcher.poll() is None and self.fetcher.poll() is None:
                # try:
                os.kill(self.fetcher.pid,SIGINT)
                time.sleep(1)
                
        if self.fetcher is not None:
            if self.fetcher.poll() is None and self.fetcher.poll() is None:
                os.kill(self.fetcher.pid,SIGTERM)
        self.fetcher = None
        try:
            wx.CallAfter(self.fetchFrame.Hide)
        except:
            pass
        
    def fetch(self, evt=None):
        import subprocess
        global titles
        global nlist
        global J
        self.fetchFrame.Show(1)
        if self.fetcher is not None:
            if self.fetcher.poll() is not None:
                self.fetcher = None
            titles = {}
            f = open(pjoin(basedir,'titles.txt'),'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                ns,title = line.split(' ',1)
                titles[int(ns)] = title[:-1].replace("\\n","\n")
            global nlist
            nlist = titles.keys()
            J = len(nlist)-1
            # print J
            return
        cmd = ("python",fetch.__file__)
        self.fetcher = subprocess.Popen(cmd,stdout=subprocess.PIPE)
        def f():
            global titles
            global nlist
            global J
            while self.fetcher and self.fetcher.poll() is None:
              try:
                # n = len(os.popen("find %s -name 'dino*.png'"%basedir).readlines())
                # print n
                time.sleep(1)
                titles = {}
                f = open(pjoin(basedir,'titles.txt'),'r')
                lines = f.readlines()
                f.close()
                for line in lines:
                    ns,title = line.split(' ',1)
                    titles[int(ns)] = title[:-1].replace("\\n","\n")
                nlist = titles.keys()
                J = len(nlist)-1
                # print "setting label"
                # if self.fetchFrame.IsShown():
                self.fetchLabel.SetLabel("%i Comics..."%(J+1))
                # print J
              except Exception,e:
                  # print e
                  pass
                  
            if self.fetcher is not None:
                self.stopFetching(None)
                # print e
        pollThread = threading.Thread(target=f)
        pollThread.start()
        # pollThread.link()
        # time.sleep(1)
        #     raise Exception("asdf")
        
        # fetch(False)
    
    def OnSave(self,evt):
        
        dlg = wx.FileDialog(self.frame, "Choose a file", self.dirname, "dinocomics.png", "*.png", \
                        wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            fp=open(os.path.join(self.dirname, self.filename),'w')
            self.image.save(fp)
            fp.close()
        dlg.Destroy()
        
    


if __name__ == '__main__':
    DC = DinoComics(0)
    DC.MainLoop()
