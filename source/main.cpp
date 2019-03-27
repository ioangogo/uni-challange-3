#include "MicroBit.h"

MicroBit uBit;

void onConnected(MicroBitEvent e)
{
    uBit.display.print("C");
    uBit.sleep(5);
    uBit.display.clear();
}

void onDisconnected(MicroBitEvent e)
{
    uBit.display.scroll("D");
}

int main()
{
    uBit.init();
    uBit.display.scroll("BLE D/N/0");

    uBit.messageBus.listen(MICROBIT_ID_BLE, MICROBIT_BLE_EVT_CONNECTED, onConnected);
    uBit.messageBus.listen(MICROBIT_ID_BLE, MICROBIT_BLE_EVT_DISCONNECTED, onDisconnected);

    new MicroBitAccelerometerService(*uBit.ble, uBit.accelerometer);
    new MicroBitButtonService(*uBit.ble);
    new MicroBitLEDService(*uBit.ble, uBit.display);
    new MicroBitTemperatureService(*uBit.ble, uBit.thermometer);
    
    release_fiber();
}
