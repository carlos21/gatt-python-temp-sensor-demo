#!/usr/bin/env python3

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from bluez import *

class SensorService(Service):

    TEST_SVC_UUID = '0a972ce6-5179-11e8-9c2d-fa7ae01bbebc'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.TEST_SVC_UUID, True)
        self.add_characteristic(HumidityCharacteristic(bus, 0, self))
        self.add_characteristic(TemperatureCharacteristic(bus, 1, self))
        

class TemperatureCharacteristic(Characteristic):

    TEMP_CHRC_UUID = '0a97304c-5179-11e8-9c2d-fa7ae01bbebc'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.TEMP_CHRC_UUID,
                ['read', 'notify'],
                service)
        self.value = []
        self.notifying = False
        self.timer = None
        
        print('init characteristic')
                
    def ReadValue(self, options):
        self.read_sensor()
        self.PropertiesChanged(GATT_CHRC_IFACE,{ 'Value': self.value }, [])
        return self.value
    
    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_temp()
        
    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self.timer.stop()
        
    def read_sensor(self):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        array = bytearray(struct.pack("f", temperature))
        self.value = dbus.ByteArray(array)
        
        print('TemperatureCharacteristic Read: ' + repr(self.value))
    
    def notify_temp(self):
        if not self.notifying:
            return
        
        if self.timer is None:
            self.timer = RepeatedTimer(0.5, self.notify_temp)
            
        self.read_sensor()
        self.PropertiesChanged(GATT_CHRC_IFACE,{ 'Value': self.value }, [])
        
        
class HumidityCharacteristic(Characteristic):

    TEMP_CHRC_UUID = 'b168025e-526c-11e8-9c2d-fa7ae01bbebc'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.TEMP_CHRC_UUID,
                ['read', 'notify'],
                service)
        self.value = []
        self.notifying = False
        self.timer = None
        print('init HumidityCharacteristic')
                
    def ReadValue(self, options):
        self.read_sensor()
        self.PropertiesChanged(GATT_CHRC_IFACE,{ 'Value': self.value }, [])
        return self.value
    
    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_humidity()
        
    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self.timer.stop()
        
    def read_sensor(self):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        array = bytearray(struct.pack("f", humidity))
        self.value = dbus.ByteArray(array)
        
        print('Humidityharacteristic Read: ' + repr(self.value))
    
    def notify_humidity(self):
        if not self.notifying:
            return
        
        if self.timer is None:
            self.timer = RepeatedTimer(0.5, self.notify_humidity)
            
        self.read_sensor()
        self.PropertiesChanged(GATT_CHRC_IFACE,{ 'Value': self.value }, [])
	