#!/usr/bin/env python3

import argparse, os, re

COORDS_RE = re.compile(r"([+-])([0-9]+)([+-])([0-9]+)")

d = {}

parser = argparse.ArgumentParser(
             prog='generate-tz-header',
             description='Generate tz-coords.h header from timezone-data')
parser.add_argument('zoneinfo_path', nargs='?', default='/usr/share/zoneinfo')
parser.add_argument('-d', '--deprecated', action='store_true')

args = parser.parse_args()
zoneTab = os.path.join(args.zoneinfo_path, 'zone.tab' if args.deprecated else 'zone1970.tab')

with open(zoneTab, "r") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        coords, tz = line.split('\t')[1:3]
        lat_sign, lat_val, long_sign, long_val = COORDS_RE.search(coords).groups()

        lat_str = lat_sign + lat_val[0:2] + "." + lat_val[2:]
        long_str = long_sign + long_val[0:3] + "." + long_val[3:]

        lat = float(lat_str)
        long = float(long_str)

        d[tz] = [lat, long]

header = """
// Generated from %s, used by csd-nightlight.c to calculate sunrise and sunset based on the system timezone

typedef struct
{
    const gchar *timezone;
    double latitude;
    double longitude;
} TZCoords;

static TZCoords tz_coord_list[] = {
""" % (zoneTab)

for zone in sorted(d.keys()):
    latitude, longitude = d[zone]

    header += "    { \"%s\", %f, %f },\n" % (zone, latitude, longitude)

header += "};"

with open("tz-coords.h", "w") as f:
    f.write(header)

quit()
