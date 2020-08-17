from csv import DictReader, excel
from dataclasses import dataclass
from math import ceil, isclose
from pathlib import Path
from typing import Callable, List

import gpxpy
from gpxpy.gpx import GPX, GPXTrackPoint, GPXWaypoint

from z1 import (EQU_PNT_PNT_FN, chk_waypoints, dd2dms, gpx_insert_lseg_closest_inplace, mkpt, Pos, tra_seg,
    vec_isclose, vec_t, WANT_DIST_M_DEFAULT, wpt_t)

assert mkpt('46.5017784 15.5537548').latitude == GPXTrackPoint(46.5017784, 15.5537548).latitude and \
    mkpt('46.5017784 15.5537548').longitude == GPXTrackPoint(46.5017784, 15.5537548).longitude

class KoceDial(excel):
    def __init__(self):
        super().__init__()
        self.skipinitialspace = True

root = Path('.').resolve()

formfeed = '\x0c'
n_formfeed = '\x0c\n'
ROUND_DMS_SD_FN_DEFAULT=lambda sd: format(round(sd, ndigits=1), '04.1f')
ROUND_DMS_SD_FN_CUT=lambda sd: format(round(sd), '02.0f')

def csv_waypoints(p: Path, t='trasa'):
    acc = []
    with open(p) as f:
        nocomm = filter(lambda row: not len(row) or row[0] != '#', f)
        reader = DictReader(nocomm, dialect=KoceDial())
        for r in reader:
            acc.append(GPXWaypoint(latitude=float(r['latitude']), longitude=float(r['longitude']), name=r['name'], symbol='http://maps.me/placemarks/placemark-red.png', type=t))
    return acc

def koce_waypoints():
    return csv_waypoints(root.joinpath('z0_koce.csv'))

def vode_waypoints():
    with open(root.joinpath('z SPP Voda.gpx'), encoding='UTF-8') as f:
        return [x for x in gpxpy.parse(f).waypoints]

with open(root.joinpath('Slovenska_Planinska_Pot_Formatted.gpx'), encoding='UTF-8') as f:
    gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(koce_waypoints())
    gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
    xm2 = gp2.to_xml()
    with open(root.joinpath('zzz_generated_2.gpx'), 'w', encoding='UTF-8') as f2:
        f2.write(xm2)

def chk_waypoints_insert_inplace(gp2: GPX, wpname: str, /, want_dist_m=WANT_DIST_M_DEFAULT):
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

@dataclass
class E():
    pnt: wpt_t
    brk: List[wpt_t]
    tra: List[wpt_t]

def eform_pre(gp2: GPX, kwp: List[wpt_t], want_dist_m=WANT_DIST_M_DEFAULT):
    chk_waypoints_insert_inplace(gp2, 'dummy_breaker', want_dist_m=want_dist_m)
    for k in kwp:
        gpx_insert_lseg_closest_inplace(gp2, GPXTrackPoint(k.latitude, k.longitude, name='dummy_koca'))

def eform(gp2: GPX, kwp: List[wpt_t], want_dist_m=WANT_DIST_M_DEFAULT):
    eform_pre(gp2, kwp, want_dist_m)

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
    CP_SUFFIX = ''
    AT_SUFFIX = ''

    d: List[str]
    ncol: int
    nrow: int
    colsep: str
    cponly: bool
    round_dms_sd_fn: Callable[[float], str]

    def __init__(self, /, ncol=5, nrow=90, colsep=' _ ', cponly=False, round_dms_sd_fn = ROUND_DMS_SD_FN_DEFAULT):
        self.d = []
        self.ncol = ncol
        self.nrow = nrow
        self.colsep = colsep
        self.cponly = cponly
        self.round_dms_sd_fn = round_dms_sd_fn
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
    def fmt_deg_dms(self, dd: float):
        d, m, sd = dd2dms(dd)
        return f'{int(d):02} {int(m):02} {self.round_dms_sd_fn(sd)}'
    def fmt_wpt(self, wpt: wpt_t):
        return f'{self.fmt_deg_dms(wpt.latitude)} {self.fmt_deg_dms(wpt.longitude)}'
    def fmt_cure(self, cure: E):
        d: List[str] = []
        for pnt in cure.tra:
            iscp = pnt.name == 'dummy_breaker'
            l = f'{self.fmt_wpt(pnt)}' + (self.CP_SUFFIX if iscp else '')
            if iscp or not self.cponly:
                d.append(l)
        d.append(f'{self.fmt_wpt(cure.pnt)}' + self.AT_SUFFIX)
        d.append(f'{cure.pnt.name}')
        return d
    def fmt_cure_thin_dbg(self, cure: E, cwps: List[E]):
        cwps_brk = [(brk, i1, i2) for i1, cwp in enumerate(cwps) for i2, brk in enumerate(cwp.brk)]
        for pnt in cure.brk:
            dd = self.fmt_wpt(pnt)
            iscp = pnt.name == 'dummy_breaker'
            isthin = any([EQU_PNT_PNT_FN(pnt, brk) for brk, _, _ in cwps_brk])
            if isthin:
                z = list(filter(lambda x: EQU_PNT_PNT_FN(pnt, x[0]), cwps_brk))
        return []
    def fmt_cure_thin(self, cure: E, cwps: List[E]):
        d: List[str] = []
        cwps_brk = [brk for cwp in cwps for brk in cwp.brk]
        for pnt in cure.brk:
            dd = self.fmt_wpt(pnt)
            iscp = pnt.name == 'dummy_breaker'
            isthin = any([EQU_PNT_PNT_FN(pnt, brk) for brk in cwps_brk])
            l = f'{self.fmt_wpt(pnt)}' + (self.CP_SUFFIX if iscp else '') + (' X' if isthin else '')
            if iscp or not self.cponly:
                d.append(l)
        d.append(f'{self.fmt_wpt(cure.pnt)}' + self.AT_SUFFIX)
        d.append(f'{cure.pnt.name}')
        return d
    def add_cure(self, cure: E):
        self.d.extend(self.fmt_cure(cure))
    def add_cure_thin(self, cure: E, cwps: List[E]):
        self.d.extend(self.fmt_cure_thin(cure, cwps))
        

def n3():
    with open(root.joinpath('Slovenska_Planinska_Pot_Formatted.gpx'), encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)

    gp2.waypoints.extend(kwp := koce_waypoints())

    lstn = eform(gp2, kwp)

    with open(root.joinpath('zzz_generated_5.txt'), 'w', encoding='UTF-8') as f2:
        pp = PriPage(cponly=True)
        for x in lstn:
            pp.add_cure(x)
        f2.write(pp.output())

    outs = []
    for x in lstn:
        pp = PriPage(cponly=True)
        pp.add_cure(x)
        outs.append(pp.output())
    with open(root.joinpath('zzz_generated_4.txt'), 'w', encoding='UTF-8') as f2:
        f2.write(n_formfeed.join(outs))

    with open(root.joinpath('zzz_generated_3.gpx'), 'w', encoding='UTF-8') as f2:
        xm2 = gp2.to_xml()
        f2.write(xm2)

if __name__ == '__main__':
    n3()
