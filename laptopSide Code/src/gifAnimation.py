
from PyQt5.QtCore import *
from time import sleep
import mBitConnection
from PIL import ImageSequence
from PIL import Image
from PIL import ImageOps

class animateer(QObject):

    def __init__(self, parent):
        super(animateer, self).__init__()
        self.parent = parent
        self.playing = False
        self.moveToThread(parent.animateThread) 

    @pyqtSlot()
    def forever_read(self):
        while True:
            while self.playing:
                for idx, frame in enumerate(self.parent.frames):
                    framebytearray=[]
                    framedata, frameDur = frame
                    for row in framedata:
                        framebytearray.append(int(row,2))
                    self.parent.showPixels_evnt.emit(framebytearray)
                    sleep(frameDur/1000)
                    if self.playing != True:
                        break

class Worker(QThread):
    showPixels_evnt = pyqtSignal(list)

    def __init__(self, connectionThread, parent, thread):
        super(Worker, self).__init__()
        parent.loadGifImage.connect(self.LoadImage)
        self.mbit = None
        self.connectionThread = connectionThread
        self.playing=False
        self.moveToThread(thread)
        self.showPixels_evnt.connect(self.connectionThread.showPixels)
        parent.changeGifState.connect(self.changePlayState)
        self.hasImage = False
        self.animater = None

    @pyqtSlot(str)
    def LoadImage(self, file):
        self.frames= self.getFrames(file)
        self.hasImage = True

    def convertoGrayScaleMBITIMG(self, img, w, h):
        grayimg = ImageOps.grayscale(img)
        px = grayimg.load()
        var = []
        for y in range(0, h):
            var.append("")
            for x in range(0, w):
                pixelVal = px[x, y]
                var[y]+="{}".format(int(pixelVal>0))
            var[y] = var[y]
        duration = img.info['duration']
        return (var,duration)

    @pyqtSlot(bool)
    def changePlayState(self, state):
        if self.animater != None:
            self.animater.playing = state
            self.playing = state

    def getFrames(self, img):
        sequence=[]

        im = Image.open(img)

        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]

        animation = ImageSequence.Iterator(im)

        arrayFrames = []
        for frame in frames:
            arrayFrames.append(self.convertoGrayScaleMBITIMG(frame, 5, 5))
        return arrayFrames

    @pyqtSlot()
    def run(self):
        self.animateThread = QThread(self, objectName='pollThread')
        self.animater= animateer(self)
        self.animateThread.started.connect(self.animater.forever_read)
        self.animateThread.start()
            