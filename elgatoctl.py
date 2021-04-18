#!/usr/bin/env python

# temp must be 2900-7000
# brightness must be 0-100

import argparse
import leglight
import sys
import yaml

template = """
---
address: {address}
port: {port}
name: {display}
brightness: {isBrightness}
power: {isOn}
temperature: {isTemperature}
"""


def save(outfile):
    lights = leglight.discover(2)
    for light in lights:
        print(template.format(**light.__dict__), file=outfile)


def load(infile):
    lights = yaml.safe_load_all(infile)
    for light in lights:
        l = leglight.LegLight(light["address"], light["port"])
        l.brightness(light["brightness"])
        l.color(light["temperature"])
        l.on() if light["power"] else l.off()


def update(iofile):
    with open(iofile, "r") as f:
        lights_in_file = list(yaml.safe_load_all(f))
    lights_discovered = leglight.discover(2)
    lights_by_name = { light.display: light for light in lights_discovered }
    for light in lights_in_file:
        name = light["name"]
        if name in lights_by_name:
            light["address"] = lights_by_name[name].address
            light["port"] = lights_by_name[name].port
        else:
            print("Warning, light {} not detected. Leaving it as is in file.".format(name))
    with open(iofile, "w") as f:
        yaml.dump_all(lights_in_file, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", nargs="?", action="append", type=argparse.FileType("r"))
    parser.add_argument("--save", nargs="?", action="append", type=argparse.FileType("w"))
    parser.add_argument("--update")
    args = parser.parse_args()
    if args.save:
        for outfile in args.save:
            if outfile is None:
                outfile=sys.stdout
            save(outfile)
            exit(0)
    if args.load:
        for infile in args.load:
            if infile is None:
                infile=sys.stdin
            load(infile)
            exit(0)
    if args.update:
        update(args.update)
        exit(0)
    if args.load is None and args.save is None:
        print("Please specify --load, --save, or --update.")
