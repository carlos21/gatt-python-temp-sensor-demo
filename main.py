#!/usr/bin/env python3

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
import Adafruit_DHT
import time
import struct
import time
import pprint

from threading import Event, Thread
from advertisement import *

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import sys

from random import randint
from bluez import *
from application import *

def register_app_cb():
    print('GATT application registered')

def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()
    
def register_ad_cb():
    print('Advertisement registered')

def register_ad_error_cb(error):
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None

def main():
    global mainloop
    global test_advertisement
    global ad_manager
    
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    app = Application(bus)

    mainloop = GObject.MainLoop()

    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                    reply_handler=register_app_cb,
                                    error_handler=register_app_error_cb)
    
    test_advertisement = TestAdvertisement(bus, 0)
    
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)
    #pprint(vars(test_advertisement))    
    #ad_manager.UnregisterAdvertisement(test_advertisement.get_path())
    #ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
    #                                 reply_handler=register_ad_cb,
    #                                 error_handler=register_ad_error_cb)

    mainloop.run()
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        ad_manager.UnregisterAdvertisement(test_advertisement.get_path())
        print('Received Keyboard interruption')