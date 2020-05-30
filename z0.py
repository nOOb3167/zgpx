from csv import DictReader, register_dialect
from dataclasses import dataclass
from math import ceil, floor, inf, isclose, sqrt
from pathlib import Path
from pprint import pprint
from typing import Callable, List, Tuple, Union

import gpxpy
from gpxpy.gpx import (GPX, GPXTrack, GPXTrackPoint, GPXTrackSegment,
                       GPXWaypoint, NearestLocationData)

from z1 import (chk_waypoints, dd2dms, gpx_insert_lseg_closest_inplace, mkpt, mkvec, Pos, tra_seg,
    vec_isclose, vec_t, WANT_DIST_M_DEFAULT, wpt_t)

assert mkpt('46.5017784 15.5537548').latitude == GPXTrackPoint(46.5017784, 15.5537548).latitude and \
    mkpt('46.5017784 15.5537548').longitude == GPXTrackPoint(46.5017784, 15.5537548).longitude

register_dialect('kocedial', 'excel', skipinitialspace=True)

root = Path('.').resolve()

formfeed = '\x0c'
n_formfeed = '\x0c\n'

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
            acc.append(GPXWaypoint(latitude=float(r['latitude']), longitude=float(r['longitude']), name=r['name'], symbol='http://maps.me/placemarks/placemark-red.png', type='trasa'))
    return acc

def vode_waypoints():
    with open(root.joinpath('z SPP Voda.gpx'), encoding='UTF-8') as f:
        return [x for x in gpxpy.parse(f).waypoints]

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

    chk_: List[D] = chk_waypoints(gp2, want_dist_m, way_fact=wf)
    chk = sorted(chk_, key=lambda x: (x.tra_idx, x.idx,), reverse=True)

    for d in chk:
        tra = gp2.tracks[d.tra_idx]
        seg = tra_seg(tra)
        seg.points.insert(d.idx + 1, GPXTrackPoint(d.vec[0], d.vec[1], name=wpname))

@dataclass
class E():
    pnt: wpt_t
    brk: List[wpt_t]
    tra: List[wpt_t]

def eform(gp2: GPX):
    kwp = koce_waypoints()

    gp2.waypoints.extend(kwp)

    chk_waypoints_insert_inplace(gp2, 'dummy_breaker')

    for k in kwp:
        gpx_insert_lseg_closest_inplace(gp2, GPXTrackPoint(k.latitude, k.longitude, name='dummy_koca'))

    def clst(a):
        nonlocal kwp
        for wp in kwp:
            if vec_isclose(wp, a):
                return wp
        raise NotImplementedError()

    lstn: List[E] = []

    for t in gp2.tracks:
        s = tra_seg(t)
        cure = E(pnt=None, brk=[], tra=[])
        for p in s.points:
            if p.name == 'dummy_koca':
                cure.pnt = p
                lstn.append(cure)
                cure = E(pnt=p, brk=[], tra=[])
            elif p.name == 'dummy_breaker':
                cure.tra.append(p)
                cure.brk.append(p)
            else:
                cure.tra.append(p)
    trunam = [clst(x.pnt) for x in lstn]
    for l, t in zip(lstn, trunam):
        l.pnt = t

    return lstn

class PriPage():
    d: List[str]
    ncol: int
    nrow: int
    colsep: str
    def __init__(self, /, ncol=5, nrow=90, colsep=' _ '):
        self.d = []
        self.ncol = ncol
        self.nrow = nrow
        self.colsep = colsep
    def output(self):
        def colrowseq(nr_):
            nc = -1
            while True:
                nc = nc + 1
                for x in range(nr_):
                    yield (nc, x)
        def padto(s: str, to: int):
            return s + ' ' * (max(0, to - len(s)))
            
        nr = len(self.d)
        nc_ = ceil(nr / self.nrow)
        nr_ = min(nr, self.nrow)

        grid = [['' for _ in range(nr_)] for c in range(nc_)]

        for x in zip(colrowseq(nr_), range(nr)):
            grid[x[0][0]][x[0][1]] = self.d[x[1]]

        longest = [len(max(c, key=lambda x: len(x))) for c in grid]

        for c in range(len(grid)):
            for r in range(len(grid[c])):
                grid[c][r] = padto(grid[c][r], longest[c]) + self.colsep

        pages = []
        for c in range(0, ceil(nc_ / self.ncol) * self.ncol, self.ncol):
            rows = [''.join(x) for x in zip(*grid[c:c+self.ncol])]
            page = '\n'.join(rows)
            pages.append(page)

        return n_formfeed.join(pages)
    @classmethod
    def fmt_deg_dms(cls, dd: float):
        d, m, sd = dd2dms(dd)
        return f'{int(d):02} {int(m):02} {round(sd, ndigits=1):04.1f}'
    @classmethod
    def fmt_wpt(cls, wpt: wpt_t):
        return f'{cls.fmt_deg_dms(wpt.latitude)} {cls.fmt_deg_dms(wpt.longitude)}'
    @classmethod
    def fmt_cure(cls, cure: E):
        d: List[str] = []
        d.append(f'{cure.pnt.name}')
        for pnt in cure.tra:
            l = f'{cls.fmt_wpt(pnt)}'
            if pnt.name == 'dummy_breaker':
                l = l + ' CP'
            d.append(l)
        return d
    def add_cure(self, cure: E):
        self.d.extend(PriPage.fmt_cure(cure))
        

def n3():
    with open(root.joinpath('Slovenska_Planinska_Pot_Formatted.gpx'), encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)

    lstn = eform(gp2)

    print(f'{lstn[63].tra=}\n{lstn[63].pnt.name=}\n{len(lstn[63].tra)=}')
    for x in range(60, 69):
        print(f'{lstn[x].pnt.name=}')

    outs = []
    for x in range(60, 69):
        pp = PriPage()
        pp.add_cure(lstn[x])
        outs.append(pp.output())
    with open(root.joinpath('zzz_generated_4.txt'), 'w', encoding='UTF-8') as f2:
        f2.write(n_formfeed.join(outs))

    with open(root.joinpath('zzz_generated_3.gpx'), 'w', encoding='UTF-8') as f2:
        xm2 = gp2.to_xml()
        f2.write(xm2)

if __name__ == '__main__':
    #z = PriPage.fmt_wpt(GPXWaypoint(45.589385, 13.861001))
    #print(f'{z=}')
    n3()
