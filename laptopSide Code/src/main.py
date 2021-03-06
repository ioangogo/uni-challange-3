from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from mBitController import Ui_MainWindow
import sys, time
from bluezero import adapter
import mBitConnection
import gifAnimation


class MainUi(QMainWindow):
    showPixels_evnt = pyqtSignal(list)
    showText_evnt = pyqtSignal(str, int)
    clear_evnt = pyqtSignal()
    connect_evnt = pyqtSignal(str, str)
    disconnect_evnt = pyqtSignal()
    startLoop= pyqtSignal()
    changeGifState= pyqtSignal(bool)

    def __init__(self):
        super(MainUi, self).__init__()
        self.acellData={"x":{"x":[], "y":[]},
        "y":{"x":[], "y":[]},
        "z":{"x":[], "y":[]}
        }
        self.xtrack=0
        self.threadpool = QThreadPool.globalInstance().setMaxThreadCount(2)
        dongles = adapter.list_adapters()
        dongle = adapter.Adapter(dongles[0])
        self.t = QThread(self, objectName='conThread')
        self.connectionThread = mBitConnection.Worker(self, self.t)
        self.connectionThread.connected.connect(self.HandelConnectEvent)
        self.connectionThread.newstate.connect(self.mBitStatusUpdate)
        self.connectionThread.disconnected.connect(self.HandeldisconnectEvent)
        self.showPixels_evnt.connect(self.connectionThread.showPixels)
        self.showText_evnt.connect(self.connectionThread.showText)
        self.clear_evnt.connect(self.connectionThread.clearMatrix)
        self.connect_evnt.connect(self.connectionThread.connectToMbit)
        self.disconnect_evnt.connect(self.connectionThread.disconnectFromMbit)
        self.t.started.connect(self.connectionThread.start)
        self.t.start()


        self.tGif = QThread(self, objectName='gifThread')
        self.gifworker=gifAnimation.Worker(self.connectionThread, self, self.tGif)
        self.tGif.started.connect(self.gifworker.run)
        self.gifworker.moveToThread(self.tGif)
        self.tGif.start()

        self.adapterAddr = str(dongle.address)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.hostMAC_txtBox.setText(self.adapterAddr)
        self.make_connection_ScrollSpeed(self.ui.scrollSpeedSlider)
        self.Buttonconnect(self.ui.connectButton, self.connectToMbit)
        self.ScrollingSpeed = 0
        
        self.ui.matrixTab.setEnabled(False)
        self.ui.miscStateTab.setEnabled(False)
        self.Buttonconnect(self.ui.openGifButton, self.loadImage)
        self.Buttonconnect(self.ui.gifStateButton, self.playgif)
        for row in self.ui.groupBox_MatrixState.findChildren(QWidget):
            for checkbox in row.findChildren(QCheckBox):
                checkbox.clicked.connect(self.handelMatrixCheckbox)
        self.Buttonconnect(self.ui.matrixClear, self.MatrixClearButton)
        self.Buttonconnect(self.ui.pushButton_showText, self.SendTextHandler)

    loadGifImage = pyqtSignal(str)

    @pyqtSlot(bool)
    def loadImage(self, state):
        self.changeGifState.emit(False)
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.loadGifImage.emit(fileName)
            self.ui.gifStateButton.setEnabled(True)


    @pyqtSlot(bool)
    def playgif(self, state):
        if self.gifworker.playing:
            self.changeGifState.emit(False)
            self.ui.gifStateButton.setText("Play")
            self.ui.openGifButton.setEnabled(True)
        else:
            self.ui.openGifButton.setEnabled(False)
            self.changeGifState.emit(True)
            self.ui.gifStateButton.setText("Stop")
            


        

    @pyqtSlot(bool)
    def SendTextHandler(self, state):
        self.showText_evnt.emit(self.ui.ShowText_LineEdit.text(),self.ScrollingSpeed)

    @pyqtSlot(bool)
    def MatrixClearButton(self, state):
        self.clear_evnt.emit()


    @pyqtSlot(bool)
    def handelMatrixCheckbox(self, state):
        rows=[]
        currentrow=0
        for row in self.ui.groupBox_MatrixState.children():
            if isinstance(row,QWidget):
                rows.append("")
                for checkbox in row.children():
                    if isinstance(checkbox,QCheckBox):
                        rows[currentrow] += str(int(checkbox.isChecked()))
                if rows[currentrow] == "":
                    rows.remove(rows[currentrow])
                else:
                    rows[currentrow] = int(rows[currentrow],2)
                    currentrow+=1
        self.showPixels_evnt.emit(rows)



    def Buttonconnect(self, ui_object, callback):
        ui_object.clicked.connect(callback)

    def make_connection_ScrollSpeed(self, slider_object):
        slider_object.valueChanged.connect(self.getScrollSpeed)

    @pyqtSlot(int)
    def getScrollSpeed(self, val):
        self.ScrollingSpeed = val
        self.ui.scrollSpeedLabel.setText(str(self.ScrollingSpeed))
        

    @pyqtSlot(dict)
    def mBitStatusUpdate(self, updateDict):
        self.ui.pushButton_mBitA.setDown(bool(updateDict["buttons"]["A"]))
        self.ui.pushButton_mBitB.setDown(bool(updateDict["buttons"]["B"]))
        self.ui.lcdNumber_temp.display(updateDict["temp"])
        self.ui.lcdNumber_X.display(updateDict["accelerometer"][0])
        self.ui.lcdNumber_Y.display(updateDict["accelerometer"][1])
        self.ui.lcdNumber_Z.display(updateDict["accelerometer"][2])

        currentPixel=0
        currentrow=0
        for row in self.ui.groupBox_MatrixState.children():
            if isinstance(row,QWidget) and not isinstance(row,QPushButton):
                matrixRow="{0:b}".format(updateDict["matrix"][currentrow]).zfill(5)
                currentPixel=0
                for checkbox in row.children():
                    if isinstance(checkbox,QCheckBox):
                        checkbox.setChecked(bool(int(matrixRow[currentPixel])))
                        currentPixel += 1
                currentrow +=1

    @pyqtSlot()
    def HandelConnectEvent(self):
        self.ui.label_connectionState.setText("Connected")
        self.ui.connectButton.setText("Disconnect")
        self.ui.statusbar.showMessage("Connected")
        self.ui.matrixTab.setEnabled(True)
        self.ui.miscStateTab.setEnabled(True)
        
    
    @pyqtSlot()
    def HandeldisconnectEvent(self):
        self.ui.label_connectionState.setText("Disconnected")
        self.ui.connectButton.setText("Connect")
        self.ui.statusbar.showMessage("Disconnected")
        self.ui.matrixTab.setEnabled(False)
        self.ui.miscStateTab.setEnabled(False)
        

    @pyqtSlot(bool)
    def connectToMbit(self, clicked):
        print(self.connectionThread.mBitconnected)
        if self.connectionThread.mBitconnected:
            self.disconnect_evnt.emit()
            print("Disconnecting")
        else:
            print("connecting")
            self.connect_evnt.emit(self.adapterAddr, self.ui.mBitMac_TxtBox.text())
            
        
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainUi()
    window.show()
    sys.exit(app.exec_())