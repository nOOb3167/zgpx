from csv import DictReader, register_dialect
from dataclasses import dataclass
from math import floor, inf, sqrt
from pathlib import Path
from typing import Callable, List, Tuple, Union

import gpxpy
from gpxpy.gpx import (GPX, GPXTrack, GPXTrackPoint, GPXTrackSegment,
                       GPXWaypoint, NearestLocationData)

from z1 import (chk_waypoints, gpx_insert_lseg_closest_inplace, mkpt, Pos, tra_seg, vec_t,
    WANT_DIST_M_DEFAULT)

assert mkpt('46.5017784 15.5537548').latitude == GPXTrackPoint(46.5017784, 15.5537548).latitude and \
    mkpt('46.5017784 15.5537548').longitude == GPXTrackPoint(46.5017784, 15.5537548).longitude

register_dialect('kocedial', 'excel', skipinitialspace=True)

root = Path('.').resolve()

frag = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
    <trk>
        <name>SPP-2 (03) Slovenska planinska pot</name>
        <cmt>Slovenska planinska pot</cmt>
        <trkseg>
            <trkpt lat="46.5019439" lon="15.5567654"/>
            <trkpt lat="46.5018308" lon="15.5564691"/>
            <trkpt lat="46.5018133" lon="15.5563194"/>
            <trkpt lat="46.5017912" lon="15.556148"/>
            <trkpt lat="46.5016229" lon="15.5556807"/>
            <trkpt lat="46.5016096" lon="15.5556273"/>
            <trkpt lat="46.5014884" lon="15.5552088"/>
            <trkpt lat="46.5015444" lon="15.5550629"/>
            <trkpt lat="46.5015366" lon="15.5549891"/>
            <trkpt lat="46.5015588" lon="15.554955"/>
            <trkpt lat="46.5015744" lon="15.5548338"/>
            <trkpt lat="46.5015731" lon="15.5547069"/>
            <trkpt lat="46.5016753" lon="15.5544166"/>
            <trkpt lat="46.5017784" lon="15.5537548"/>
            <trkpt lat="46.5018456" lon="15.5531275"/>
            <trkpt lat="46.5019852" lon="15.5525686"/>
        </trkseg>
    </trk>
</gpx>
'''

def koce_waypoints():
    acc = []
    with open(root.joinpath('z0_koce.csv')) as f:
        reader = DictReader(f, dialect='kocedial')
        for r in reader:
            acc.append(GPXWaypoint(latitude=r['latitude'], longitude=r['longitude'], name=r['name'], symbol='http://maps.me/placemarks/placemark-red.png', type='trasa'))
    return acc

def vode_waypoints():
    with open(root.joinpath('z SPP Voda.gpx'), encoding='UTF-8') as f:
        return [x for x in gpxpy.parse(f).waypoints]

gpx = gpxpy.parse(frag)
gpxt: GPXTrack = gpx.tracks[0]
nl = gpxt.get_nearest_location(GPXTrackPoint(46.5017784, 15.5537548-0.0004))
print(nl)

gpx_insert_lseg_closest_inplace(gpx, GPXTrackPoint(46.5017784, 15.5537548-0.0004))

gpx.waypoints.extend(koce_waypoints())
gpx.waypoints.extend(vode_waypoints())
gpx.waypoints.extend(chk_waypoints(gpx))

xml = gpx.to_xml()

with open(root.joinpath('zzz_generated.gpx'), 'w', encoding='UTF-8') as f:
    f.write(xml)


with open(root.joinpath('Slovenska_Planinska_Pot_Formatted.gpx'), encoding='UTF-8') as f:
    gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(koce_waypoints())
    gp2.waypoints.extend(chk_waypoints(gp2))
    xm2 = gp2.to_xml()
    with open(root.joinpath('zzz_generated_2.gpx'), 'w', encoding='UTF-8') as f2:
        f2.write(xm2)

def chk_waypoints_insert_inplace(gp2: GPX, wpname: str, want_dist_m=WANT_DIST_M_DEFAULT):
    @dataclass
    class D():
        vec: vec_t
        idx: int
        tra_idx: int
    def wf(pos: Pos, vec: vec_t):
        return D(vec, pos.idx, pos.tra_idx)

    chk_: List[D] = chk_waypoints(gp2, want_dist_m=want_dist_m, way_fact=wf)
    chk = sorted(chk_, key=lambda x: (x.tra_idx, x.idx,), reverse=True)
    
    for d in chk:
        tra = gp2.tracks[d.tra_idx]
        seg = tra_seg(tra)
        seg.points.insert(d.idx + 1, GPXTrackPoint(d.vec[0], d.vec[1], name=wpname))

def n3():
    with open(root.joinpath('Slovenska_Planinska_Pot_Formatted.gpx'), encoding='UTF-8') as f:
        kwp = koce_waypoints()

        gp2 = gpxpy.parse(f)
        gp2.waypoints.extend(kwp)

        @dataclass
        class D():
            vec: vec_t
            idx: int
            tra_idx: int
        def wf(pos: Pos, vec: vec_t):
            return D(vec, pos.idx, pos.tra_idx)

        chk_: List[D] = chk_waypoints(gp2, way_fact=wf)
        chk = sorted(chk_, key=lambda x: (x.tra_idx, x.idx,), reverse=True)
        for d in chk:
            tra = gp2.tracks[d.tra_idx]
            seg = tra_seg(tra)
            seg.points.insert(d.idx + 1, GPXTrackPoint(d.vec[0], d.vec[1], name='dummy_breaker'))

        for d in chk:
            gp2.waypoints.append(GPXWaypoint(d.vec[0], d.vec[1], symbol='http://maps.me/placemarks/placemark-yellow.png'))

    with open(root.joinpath('zzz_generated_3.gpx'), 'w', encoding='UTF-8') as f2:
        xm2 = gp2.to_xml()
        f2.write(xm2)

        # for d in chk:
        #     tra = gp2.tracks[d.tra_idx]
        #     seg = tra_seg(tra)

        # gp2.waypoints.extend()

        # gpx_insert_lseg_closest_inplace()
n3()
