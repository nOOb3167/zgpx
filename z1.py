from math import inf, isclose, sqrt

from gpxpy.gpx import (GPX, GPXTrack, GPXTrackPoint, GPXTrackSegment,
                       GPXWaypoint)
from typing import Any, Callable, List, Tuple, Union

WANT_DIST_M_DEFAULT = 2000

wpt_t = Union[GPXWaypoint, GPXTrackPoint]
vec_t = Union[wpt_t, list, tuple]

wpt_t_default = lambda p,v: GPXWaypoint(v[0], v[1], symbol='http://maps.me/placemarks/placemark-green.png', type='checkpoint')

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

def vec_add(a: List, b: List):
    return [a[0] + b[0], a[1] + b[1]]

def vec_sub(a: List, b: List):
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

def mkvec(pnt):
    if isinstance(pnt, GPXTrackPoint) or isinstance(pnt, GPXWaypoint):
        return [pnt.latitude, pnt.longitude]
    elif (isinstance(pnt, tuple) or isinstance(pnt, list)) and len(pnt) == 2:
        return pnt
    else:
        raise RuntimeError()

def mkpt(s: str):
    t = s.split(sep=' ', maxsplit=1)
    return GPXTrackPoint(float(t[0]), float(t[1]))

def tra_seg(tra: GPXTrack) -> GPXTrackSegment:
    assert len(tra.segments) == 1
    return tra.segments[0]

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

def pnt_lineseg_dist(pt_, segS_, segE_):
    """https://onlinemschool.com/math/assistance/vector/projection/"""
    pt, segS, segE = mkvec(pt_), mkvec(segS_), mkvec(segE_)

    a = vec_sub(pt, segS)
    b = vec_sub(segE, segS)
    a_dot_b = vec_dot(a, b)
    b_len = vec_len(b)
    
    a_proj_b__magnitude = a_dot_b / b_len if not isclose(b_len, 0.0, rel_tol=0.0, abs_tol=1e-4) else -inf

    if a_proj_b__magnitude < 0.0:
        return vec_len(vec_sub(pt, segS))
    elif a_proj_b__magnitude > b_len:
        return vec_len(vec_sub(pt, segE))
    else:
        b_unit = vec_unit(b)
        return vec_len(vec_sub(a, vec_scale(b_unit, a_proj_b__magnitude)))

class Pos():
    tra: GPXTrack
    tra_idx: int
    idx: int
    segS: GPXTrackPoint
    segE: GPXTrackPoint
    _dist_seg: float
    pos: float
    def __init__(self, trl: List[GPXTrack], tra_idx: int):
        assert len(tra_seg(trl[tra_idx]).points) > 2
        self.tra = trl[tra_idx]
        self.tra_idx = tra_idx
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
    def waypointat(self, way_fact):
        vS, vE = mkvec(self.segS), mkvec(self.segE)
        vQ = vec_scale(vec_sub(vE, vS), self.pos / self._dist_seg)
        v = vec_add(vS, vQ)
        return way_fact(self, v)

def chk_waypoints(gpx: GPX, want_dist_m=WANT_DIST_M_DEFAULT, /, way_fact: Callable[[Pos, vec_t], Any] = wpt_t_default):
    wpt: List[Any] = []
    remain = None
    def remain_reset():
        nonlocal remain
        remain = want_dist_m
    for tra_idx in range(len(gpx.tracks)):
        remain_reset()
        pos = Pos(gpx.tracks, tra_idx)
        while not pos.atend_idxpos():
            remain = pos.try_advance(remain)
            if not (remain > 0):
                remain_reset()
                wpt.append(pos.waypointat(way_fact))
    return wpt

if __name__ == '__main__':
    import sys
    print(sys.argv)
    ta = GPXTrackPoint(46.533183, 15.628635)
    tb = GPXTrackPoint(46.523701563527474, 15.62096270039927)
    tc = GPXTrackPoint(46.523663, 15.626323)
    print(tc.distance_2d(ta))
    print(tc.distance_2d(tb))

    q = GPXTrackPoint(12, 12)
    w = GPXWaypoint(12, 12)
    q_ = mkvec(q)
    w_ = mkvec(w)
    print(q_)
    print(w_)