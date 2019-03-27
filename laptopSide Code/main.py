import gatt, time, dbus
import animation

LEDSERVICE_SERVICE_UUID = "E95DD91D251D470AA062FA1922DFA9A8"
LEDMATRIXSTATE_CHARACTERISTIC_UUID = "E95D7B77251D470AA062FA1922DFA9A8"



manager = gatt.DeviceManager(adapter_name='hci0')

LED_MATRIX_SERVICE = None
LED_STATE_Characteristic = None

frames=None


class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        global LED_MATRIX_SERVICE
        global LED_STATE_Characteristic
        
        LED_MATRIX_SERVICE = next(
            s for s in device.services
            if s.uuid == 'e95dd91d-251d-470a-a062-fa1922dfa9a8'
        )

        LED_STATE_Characteristic = next(
            c for c in LED_MATRIX_SERVICE.characteristics
            if c.uuid == 'e95d7b77-251d-470a-a062-fa1922dfa9a8')

        print(LED_STATE_Characteristic.read_value())
        while True:
            for idx, frame in enumerate(frames):
                framebytearray=[]
                framedata, frameDur = frame
                for row in framedata:
                    framebytearray.append(dbus.Byte(int(row,2)))
                LED_STATE_Characteristic.write_value(framebytearray)
                time.sleep(frameDur/1000)
                print(idx+1)

        def characteristic_value_updated(self, characteristic, value):
            print("{}: {}".format(characteristic.service,value.decode("utf-8")))
        
        def characteristic_write_value_failed(error):
            print(error)

        
        
frames = animation.getFrames("test.gif")
            
device = AnyDevice(mac_address='CF:33:A2:FF:C5:1D', manager=manager)
device.connect()
manager.run()




# device.char_write(LEDMATRIXSTATE_CHARACTERISTIC_UUID,frame)
