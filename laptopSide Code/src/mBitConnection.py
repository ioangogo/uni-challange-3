
from PyQt5.QtCore import *
from time import sleep
import main
from bluezero import microbit

class poller(QObject):

    def __init__(self, parent):
        super(poller, self).__init__()
        self.parent = parent
        self.stateDict = {"matrix":[],
        "buttons":{"A": False, "B":False},
        "accelerometer":[],
        "temp":0}
        self.moveToThread(parent.pollingThread) 


    data_ready = pyqtSignal(object)

    @pyqtSlot()
    def forever_read(self):
        while True:
            if self.parent.mbit != None:
                if self.parent.mBitconnected:
                    self.InLoop = True
                    self.stateDict["matrix"]=self.parent.mbit.pixels
                    self.stateDict["accelerometer"] = self.parent.mbit.accelerometer
                    self.stateDict["buttons"]["A"] = self.parent.mbit.button_a
                    self.stateDict["buttons"]["B"] = self.parent.mbit.button_b
                    self.stateDict["temp"]=self.parent.mbit.temperature
                    if self.parent.waitTillSet != True:
                        self.data_ready.emit(self.stateDict)
                    self.InLoop = False

class Worker(QObject):
    newstate = pyqtSignal(dict)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, parent, thread):
        super(Worker, self).__init__()
        self.mbit = None
        self.mBitconnected = False
        self.paused = False
        self.waitTillSet = False
        self.playingGif = False
        self.InLoop=False
        self.stateDict = {"matrix":[],
        "buttons":{"A": False, "B":False},
        "accelerometer":[],
        "temp":0}

        self.moveToThread(thread)

    @pyqtSlot(dict)
    def handleData(self, newData):
        self.stateDict = newData
        self.newstate.emit(newData)
    
    @pyqtSlot(list)
    def showPixels(self, pixelArray):
        self.mbit.pixels = pixelArray
        
            
    @pyqtSlot(str,int)
    def showText(self, msg, scrollSpeed):
        self.mbit.scroll_delay = scrollSpeed
        self.mbit.text = msg

    @pyqtSlot()
    def clearMatrix(self):
        self.mbit.clear_display()

    @pyqtSlot(str, str)
    def connectToMbit(self, adapterMac, mbitMac):
        print(adapterMac, mbitMac)
        try:
            self.mbit = microbit.Microbit(
                            adapter_addr=adapterMac,
                            device_addr=mbitMac, 
                            accelerometer_service=True,
                            button_service=True,
                            led_service=True,
                            magnetometer_service=False,
                            pin_service=False,
                            temperature_service=True
                            )
        
            self.mbit.connect()
        except Exception as e:
            print(e)
            self.stop()
        finally:
            self.connected.emit()
            self.mBitconnected = True
            self.paused = False
    
    @pyqtSlot()
    def disconnectFromMbit(self):
        if self.mbit != None:
            if self.mbit.connected:
                self.paused = True
                while self.InLoop:
                    pass
                self.mbit.disconnect()
                self.disconnected.emit()
                self.mBitconnected = False
    @pyqtSlot()
    def start(self):
        self.pollingThread = QThread(self, objectName='pollThread')
        self.poller = poller(self)
        self.poller.data_ready.connect(self.handleData)
        self.pollingThread.started.connect(self.poller.forever_read)
        self.pollingThread.start()

