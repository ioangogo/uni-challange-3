
from PyQt5.QtCore import *
from time import sleep
import main
from bluezero import microbit

class Worker(QThread):
    newstate = pyqtSignal(dict)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self):
        self.mbit = None
        QThread.__init__(self)
        self.stateDict = {"matrix":[],
        "buttons":{"A": False, "B":False},
        "accelerometer":[],
        "temp":0}
        self.mBitconnected = False
        self.paused = False
        self.InLoop=False

    def __del__(self):
        self.stop()
    
    def stop(self):
        self.wait()
    
    @pyqtSlot(list)
    def showPixels(self, pixelArray):
        self.mbit.pixels = pixelArray
        while not self.stateDict["matrix"] == pixelArray:
            pass
            
        
    @pyqtSlot(str,int)
    def showText(self, msg, scrollSpeed):
        self.mbit.scroll_delay = scrollSpeed
        self.mbit.text = msg

    @pyqtSlot()
    def clearMatrix(self):
        self.mbit.clear_display()

    @pyqtSlot(str, str)
    def connectToMbit(self, adapterMac, mbitMac):
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
        try:
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

    def run(self):
        while True:
            if self.mBitconnected and not self.paused:
                self.InLoop = True
                self.stateDict["matrix"]=self.mbit.pixels
                self.stateDict["accelerometer"] = self.mbit.accelerometer
                self.stateDict["buttons"]["A"] = self.mbit.button_a
                self.stateDict["buttons"]["B"] = self.mbit.button_b
                self.stateDict["temp"]=self.mbit.temperature
                if not self.paused:
                    self.newstate.emit(self.stateDict)
                self.InLoop = False
                sleep(0.005)