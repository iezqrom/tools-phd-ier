#!/usr/bin/env python3
# MY CODE
try:
    import globals
except:
    pass
from grabPorts import grabPorts
from classes_text import *
from failing import *
from saving_data import *

# OTHER'S CODE
from datetime import datetime
import time
from time import sleep

try:
    import sys
except:
    pass
try:
    import tty
except:
    pass
try:
    import termios
except:
    pass

import glob
import keyboard
import serial

try:
    import winsound
except:
    pass
try:
    import os
except:
    pass
import numpy as np
import pandas as pd
import curses
import re
import struct
from scipy import signal


class ArdUIno(grabPorts):
    def __init__(
        self, winPort=None, num_ards=1, usb_port=None, n_modem=None, name="Arduino"
    ):

        self.ports = grabPorts()
        self.n_modem = n_modem
        self.usb_port = usb_port
        self.name = name
        self.ports.arduinoPort(winPort, num_ards, usb_port, self.n_modem)
        # printme(f'Arduino port: {print_var_name(self)}')
        print(str(self.ports.arduino_ports))

        if num_ards == 1:
            try:
                self.arduino = serial.Serial(
                    self.ports.arduino_ports[0], 9600, timeout=1
                )
            except IndexError:
                print("I cannot find any arduino boards!")
        elif num_ards > 1:
            self.arduino1 = serial.Serial(self.ports.arduino_ports[0], 9600, timeout=1)
            self.arduino2 = serial.Serial(self.ports.arduino_ports[1], 9600, timeout=1)

        self.arduino.flushInput()

    def readData(self, dataParser=float):
        self.read_parsed = None

        try:
            self.read = self.arduino.readline()
            self.read_parsed = dataParser(self.read)

        except Exception as e:
            print(f"Exception from arduino readData method {e}")


    def OpenClose(self, wait_close, wait_open, devices=None):

        if devices != None:
            devices[0].device.move_abs(globals.posX)
            devices[1].device.move_abs(globals.posY)
            devices[2].device.move_abs(globals.posZ)

        while True:

            try:

                time.sleep(wait_close * 1 / 10)

                globals.stimulus = 1
                self.arduino.write(struct.pack(">B", globals.stimulus))

                time.sleep(wait_open)

                globals.stimulus = 0
                self.arduino.write(struct.pack(">B", globals.stimulus))

                time.sleep(wait_close * 9 / 10)

                globals.counter += 1

                if globals.counter == 3:
                    globals.stimulus = 0
                    self.arduino.write(struct.pack(">B", globals.stimulus))
                    break
                # if keyboard.is_pressed('e'):
                #
                #     globals.stimulus = 0
                #     self.arduino.write(struct.pack('>B', globals.stimulus))
                #     break

            except KeyboardInterrupt:
                sys.exit(1)

    def controlShu(self, devices):

        while True:
            try:

                if keyboard.is_pressed("c"):
                    globals.stimulus = 0
                    self.arduino.write(struct.pack(">B", globals.stimulus))

                if keyboard.is_pressed("o"):
                    globals.stimulus = 1
                    self.arduino.write(struct.pack(">B", globals.stimulus))

                if keyboard.is_pressed("u"):
                    devices["colther"][0].device.move_rel(-20000)

                if keyboard.is_pressed("d"):
                    devices["colther"][0].device.move_rel(20000)

                if keyboard.is_pressed("e"):

                    globals.stimulus = 0
                    self.arduino.write(struct.pack(">B", globals.stimulus))
                    break

                try:
                    pos = devices["colther"][0].device.send("/get pos")
                    globals.pos = int(pos.data)
                except:
                    pass
            except KeyboardInterrupt:
                sys.exit(1)

    def OpenCloseMoL(self, event):
        """
        Method to perform Method of Limits with the shutter
        """

        if event != None:
            event.wait()

        globals.stimulus = 2

        if event != None:
            event.clear()

        self.arduino.write(struct.pack(">B", globals.stimulus))
        printme("Start reaction time")
        start = time.time()
        # time.sleep(0.2)

        while True:
            time.sleep(0.001)
            if globals.stimulus == 4:
                globals.rt = time.time() - start
                self.arduino.write(struct.pack(">B", globals.stimulus))
                # time.sleep(0.1)
                break

    def readFloat(self, start, finish, globali, event):
        while True:
            read = self.arduino.readline()
            cropp = read[start:finish]
            # print(read)
            try:
                float_cropp = float(cropp)
                rounded_float_cropp = round(float_cropp, 3)

                globali.set(rounded_float_cropp)
            except Exception as e:
                print(e)

            if keyboard.is_pressed("enter"):
                event[0].set()
                break
            elif keyboard.is_pressed("l"):
                event[0].set()
                # print('Waiting for Zaber to move')
                event[1].wait()

    def closeOpenTemp(self, range):
        """
        Method of function to close and open shutter depending on the temperature
        """

        while True:
            # print(globals.temp)
            if globals.temp < range[0]:
                # print('Close')
                globals.stimulus = 0
                self.arduino.write(struct.pack(">B", globals.stimulus))
            elif globals.temp > range[1]:
                # print('Open')
                globals.stimulus = 1
                self.arduino.write(struct.pack(">B", globals.stimulus))

            if globals.momen > globals.timeout:
                printme("Finish shutter")
                globals.stimulus = 0
                self.arduino.write(struct.pack(">B", globals.stimulus))
                break

    def readDistance(self):
        """
        Method to read distance and save it during a period set manually
        """
        self.buffer = []
        save_buffer = False
        pressed = False
        while True:
            #
            read = self.arduino.readline()
            if save_buffer:
                self.buffer.append(float(read))
            try:
                print(float(read))
            except:
                printme("Arduino sent garbage")

            if keyboard.is_pressed("e"):
                printme("Done reading distance...")
                break
            elif keyboard.is_pressed("s"):
                if not pressed:
                    printme("STARTED saving readings from Arduino")
                    save_buffer = True
                    pressed = True
            elif keyboard.is_pressed("o"):
                if not pressed:
                    printme("STOPPED saving readings from Arduino")
                    save_buffer = False
                    pressed = True
            else:
                pressed = False


################################################################################
############################# FUNCTIONS #########################################
################################################################################


def reLoad(ard):
    os.system("clear")
    was_pressed = False
    print('\nPosition syringe pusher ("d" for down / "u" for up / "e" to move on)\n')
    while True:
        if keyboard.is_pressed("e"):
            break

        elif keyboard.is_pressed("d"):
            if not was_pressed:
                try:
                    globals.stimulus = 6
                    ard.arduino.write(struct.pack(">B", globals.stimulus))
                except Exception as e:
                    errorloc(e)
                was_pressed = True

        elif keyboard.is_pressed("u"):
            if not was_pressed:
                try:
                    globals.stimulus = 5
                    ard.arduino.write(struct.pack(">B", globals.stimulus))
                except Exception as e:
                    errorloc(e)
                was_pressed = True
        else:
            was_pressed = False


def shakeShutter(ard, times):
    for i in np.arange(times):
        globals.stimulus = 1
        ard.arduino.write(struct.pack(">B", globals.stimulus))
        printme("Open shutter")

        time.sleep(0.2)

        globals.stimulus = 0
        ard.arduino.write(struct.pack(">B", globals.stimulus))

        printme("Close shutter")
        time.sleep(0.2)


def tryexceptArduino(ard, signal):
    try:
        ard.arduino.write(struct.pack(">B", signal))
        print(f"TALKING TO {ard.name}")
        time.sleep(0.1)

    except Exception as e:
        os.system("clear")
        errorloc(e)
        waitForEnter(f"\n\n Press enter when {ard.name} is fixed...")
        ard = ArdUIno(usb_port=ard.usb_port, n_modem=ard.n_modem)
        ard.arduino.flushInput()
        time.sleep(1)
        ard.arduino.write(struct.pack(">B", signal))
        time.sleep(0.1)

    if signal == 6:
        file_name = "./data/pusher_counter"
        file = open(file_name)
        old_value = int(file.read())
        old_value += 1
        writeValue("./data/pusher_counter", old_value)


def movePanTilt(ard, trio_array, trigger_move=8):
    printme(
        f"Sending to PanTilt x: {trio_array[0]}, y: {trio_array[1]}, z: {trio_array[2]}"
    )
    try:
        ard.arduino.write(struct.pack(">B", trigger_move))
        time.sleep(globals.keydelay)
        ard.arduino.write(
            struct.pack(">BBB", trio_array[0], trio_array[1], trio_array[2])
        )
    except Exception as e:
        os.system("clear")
        errorloc(e)
        waitForEnter(f"\n\n Press enter when Arduino PanTilt is fixed...")
        ard = ArdUIno(
            usb_port=globals.usb_port_pantilt, n_modem=globals.modem_port_pantilt
        )
        ard.arduino.flushInput()
        time.sleep(1)
        ard.arduino.write(struct.pack(">B", trigger_move))
        time.sleep(globals.keydelay)
        ard.arduino.write(
            struct.pack(">BBB", trio_array[0], trio_array[1], trio_array[2])
        )

    print("TALKING TO PANTILT")


Fs = 20
# sampling freq
Fc = 2
# cutoff
[b, a] = signal.butter(2, Fc / (Fs / 2))


def smoother(datapoint):
    d_cen_round_filtered = (
        b[0] * data2[-1]
        + b[1] * data2[-2]
        + b[2] * data2[-3]
        - a[1] * df2[-1]
        - a[2] * df2[-2]
    )


def print_var_name(variable):
    for name in globals():
        if eval(name) == variable:
            print(name)
