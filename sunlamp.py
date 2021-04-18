#!/usr/bin/env python

import leglight
import os
import time
import sys


light = None
light_name = os.environ.get("SUNLAMPNAME")
if light_name is None:
    print("⚠️ Please set environment variable SUNLAMPNAME.")
    print("ℹ️ Use the 'scan' command to scan for available lamp names.")
else:
    for l in leglight.discover(2):
        if l.display == light_name:
            light = l
    if light is None:
        print("⚠️ Sorry, I could not find a light named {}.".format(light_name))
    else:
        print("💡Detected {}.".format(light))


# First element = brightness (range: 0-100)
# Second element = temperature (range: 2900-7000)
day = (90, 6000)
night = (1, 3000)


# (hour,minute)
sunrise_begin = (7, 0)
sunrise_end = (7, 30)
sunset_begin = (19, 0)
sunset_end = (22, 0)


# hm1, hm2, hmnow, should be tuples with (hour,minute)
# v1 and v2 should be tuples with (brightness,temp)
def interpolate(hm1, hm2, hmnow, v1, v2):
    t1 = hm1[0]*60 + hm1[1]
    t2 = hm2[0]*60 + hm2[1]
    tnow = hmnow[0]*60 + hmnow[1]
    fraction = (tnow - t1) / (t2 - t1)
    return (
        int(v1[0] + fraction*(v2[0]-v1[0])),
        int(v1[1] + fraction*(v2[1]-v1[1])),
        )


def calc(hh, mm):
    # returns a tuple with (brightness, temp) according to current time
    now = (hh, mm)
    if now < sunrise_begin:
        return night
    if now < sunrise_end:
        return interpolate(sunrise_begin, sunrise_end, now, night, day)
    if now < sunset_begin:
        return day
    if now < sunset_end:
        return interpolate(sunset_begin, sunset_end, now, day, night)
    return night


def once():
    now = time.localtime()
    brightness, temperature = calc(now.tm_hour, now.tm_min)
    light.brightness(brightness)
    light.color(temperature)


def run():
    while True:
        once()
        time.sleep(60)


def dryrun():
    midnight = int(time.mktime((0, 0, 0, 0, 0, 0, 0, 0, 0)))
    for i in range(midnight, midnight+3600*24, 300):
        now = time.localtime(i)
        h, m = now.tm_hour, now.tm_min
        b, t = calc(h, m)
        print("{:02}:{:02} {} {}".format(h, m, b, t))


def quicktest():
    midnight = int(time.mktime((0, 0, 0, 0, 0, 0, 0, 0, 0)))
    oldb, oldt = None, None
    for i in range(midnight, midnight+3600*24, 60):
        now = time.localtime(i)
        h, m = now.tm_hour, now.tm_min
        b, t = calc(h, m)
        print("{:02}:{:02} {} {}".format(h, m, b, t))
        if b == oldb and t == oldt:
            time.sleep(0.01)
        else:
            light.brightness(b)
            light.color(t)
            time.sleep(1)
        oldb, oldt = b, t


def scan():
    for l in leglight.discover(2):
        print("💡" + l.display)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ℹ️Available commands:")
        for func_name, func in list(globals().items()):
            if callable(func) and func.__code__.co_argcount==0:
                print("🖥️" + func_name)
        exit(0)
    func_name = sys.argv[1]
    func = globals()[func_name]
    func()
