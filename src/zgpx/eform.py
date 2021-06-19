from dataclasses import dataclass
from gpxpy.gpx import GPX, GPXTrackPoint
from math import ceil
from typing import Callable, List
from zgpx.ptutil import chk_waypoints_insert_inplace, dd2dms, gpx_insert_lseg_closest_inplace, tra_seg, vec_isclose
from zgpx.util import EQU_PNT_PNT_FN, WANT_DIST_M_DEFAULT, n_formfeed, ROUND_DMS_SD_FN_DEFAULT, wpt_t

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
