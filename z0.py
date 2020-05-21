from csv import DictReader, register_dialect
from dataclasses import dataclass
from math import floor, inf, sqrt
from pathlib import Path
from typing import List, Tuple, Union

import gpxpy
from gpxpy.gpx import (GPX, GPXTrack, GPXTrackPoint, GPXTrackSegment,
                       GPXWaypoint, NearestLocationData)

vec_t = Union[GPXWaypoint, GPXTrackPoint, list, tuple]

'''
https://github.com/stesalati/TrackAnalyser/blob/master/bombo.py#L1047
    dms2dd / dd2dms
'''

def dms2dd(degrees, minutes, seconds, direction):
    dd = degrees + minutes/60 + seconds/(60*60)
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def old():
    with open(root.joinpath('Slovenska_Planinska_Pot_Formatted.gpx')) as f:
        gpx = gpxpy.parse(f)
        pts = [w for q in gpx.tracks for w in q.segments if len(w.points) > 1]
        for t in gpx.tracks:
            for s in t.segments:
                print(len(s.points))


register_dialect('kocedial', 'excel', skipinitialspace=True)

root = Path('C:/Users/Andrej/test/snw/zgpx/')

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


def mkpt(s: str):
    t = s.split(sep=' ', maxsplit=1)
    return GPXTrackPoint(float(t[0]), float(t[1]))

def mkvec(pnt):
    if isinstance(pnt, GPXTrackPoint) or isinstance(pnt, GPXWaypoint):
        return [pnt.latitude, pnt.longitude]
    elif (isinstance(pnt, tuple) or isinstance(pnt, list)) and len(pnt) == 2:
        return pnt
    else:
        raise RuntimeError()

def tra_seg(tra: GPXTrack) -> GPXTrackSegment:
    assert len(tra.segments) == 1
    return tra.segments[0]

def prevnext(t: GPXTrack, u: NearestLocationData):
    s = t.segments[u.segment_no]
    p1i = max(u.point_no - 1, 0)
    p2i = min(u.point_no + 1, max(len(s.points) - 1, 0))
    return None

def tra_iter_pts(tra: GPXTrack) -> Tuple[int, GPXTrackPoint, GPXTrackPoint]:
    seg = tra_seg(tra)
    for idx in range(max(len(seg.points) - 1, 0)):
        yield (idx, seg.points[idx], seg.points[idx+1],)

def gpx_find_tra_dist_min(gpx: GPX, pnt: vec_t) -> GPXTrack:
    return min([(tra_find_pnt_dist(tra, pnt), tra,) for tra in gpx.tracks], key=lambda x: x[0])[1]

def tra_find_pnt_dist(tra: GPXTrack, pnt: vec_t):
    return min([pnt_lineseg_dist(pnt, segS, segE) for idx, segS, segE in tra_iter_pts(tra)])

def tra_find_lseg_idx_closest(tra: GPXTrack, pnt: vec_t) -> int:
    return min([(pnt_lineseg_dist(pnt, segS, segE), idx,) for idx, segS, segE in tra_iter_pts(tra)], key=lambda x: x[0])[1]

def gpx_insert_lseg_closest_inplace(gpx: GPX, pnt: GPXTrackPoint):
    tra = gpx_find_tra_dist_min(gpx, pnt)
    idx = tra_find_lseg_idx_closest(tra, pnt)
    tra_seg(tra).points.insert(idx + 1, pnt)

def vec_minus(a: List, b: List):
    return [a[0] - b[0], a[1] - b[1]]

def vec_len(a: List):
    return sqrt(a[0]*a[0] + a[1]*a[1])

def vec_scale(a: List, b: float):
    return [a[0] * b, a[1] * b]

def vec_unit(a: List):
    if (len := vec_len(a)) == 0.0:
        raise RuntimeError()
    else:
        return [a[0] / len, a[1] / len]

def vec_dot(a: List, b: List):
    return (a[0] * b[0]) + (a[1] * b[1])

def pnt_lineseg_dist(pt_, segS_, segE_):
    """https://onlinemschool.com/math/assistance/vector/projection/"""
    pt, segS, segE = mkvec(pt_), mkvec(segS_), mkvec(segE_)
    a = vec_minus(pt, segS)
    b = vec_minus(segE, segS)
    a_dot_b = vec_dot(a, b)
    b_len = vec_len(b)
    a_proj_b__magnitude = a_dot_b / b_len

    if a_proj_b__magnitude < 0.0:
        return vec_len(vec_minus(pt, segS))
    elif a_proj_b__magnitude > b_len:
        return vec_len(vec_minus(pt, segE))
    else:
        b_unit = vec_unit(b)
        return vec_len(vec_minus(pt, vec_scale(b_unit, a_proj_b__magnitude)))

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

def chk_waypoints(gpx: GPX, want_dist_m=2000):
    class Pos:
        tra: GPXTrack
        idx: int
        segS: GPXTrackPoint
        segE: GPXTrackPoint
        _dist_seg: float
        pos: float
        def __init__(self, tra):
            assert len(tra_seg(tra).points) > 2
            self.tra = tra
            self.idx = -1
            self.nextidx()
        def nextidx(self):
            self.idx = self.idx + 1
            self.segS = tra_seg(self.tra).points[self.idx]
            self.segE = tra_seg(self.tra).points[self.idx+1]
            self._dist_seg = self.segS.distance_2d(self.segE)
            self.pos = 0.0
        def try_advance(self, remain):
            endpos = min(self.pos + remain, self._dist_seg)
            remain -= (endpos - self.pos)
            self.pos = endpos
            if self.atend_pos():
                if not self.atend_idx():
                    self.nextidx()
            return remain
        def atend_idx(self):
            return self.idx == len(tra_seg(self.tra).points) - 2
        def atend_pos(self):
            return not (self.pos < self._dist_seg)
        def atend_idxpos(self):
            return self.atend_idx() and self.atend_pos()
        def waypointat(self):
            vS, vE = mkvec(self.segS), mkvec(self.segE)
            vQ = vec_scale(vec_minus(vE, vS), self.pos / self._dist_seg)
            return GPXWaypoint(latitude=vS[0]+vQ[0], longitude=vS[1]+vQ[1], symbol='http://maps.me/placemarks/placemark-green.png', type='checkpoint')
    wpt: List[GPXWaypoint] = []
    remain = None
    def remain_reset():
        nonlocal remain
        remain = want_dist_m
    for tra in gpx.tracks:
        remain_reset()
        pos = Pos(tra)
        while not pos.atend_idxpos():
            remain = pos.try_advance(remain)
            if not (remain > 0):
                remain_reset()
                wpt.append(pos.waypointat())
    return wpt

assert mkpt('46.5017784 15.5537548').latitude == GPXTrackPoint(46.5017784, 15.5537548).latitude and \
    mkpt('46.5017784 15.5537548').longitude == GPXTrackPoint(46.5017784, 15.5537548).longitude

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

# def insert_closest_inplace(gpx: GPX, pnt: GPXTrackPoint):
#     lseg = []
#     lidx = []
#     ldst = []
#     for tra in gpx.tracks:
#         for seg in tra.segments:
#             nit = max(len(seg.points) - 1, 0)
#             for idx in range(nit):
#                 lseg.append(seg)
#                 lidx.append(idx)
#                 ldst.append(pnt_lineseg_dist(pnt, seg.points[idx], seg.points[idx+1]))
#     #
#     dmin: Tuple[GPXTrackSegment, int, float] = (None, None, inf)
#     for w in zip(lseg, lidx, ldst):
#         if (w[2] < dmin[2]):
#             dmin = w
#     assert dmin[2] != inf
#     #
#     dmin[0].points.insert(dmin[1]+1, pnt)
