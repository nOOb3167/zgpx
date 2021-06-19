from csv import DictReader as DR, excel
from gpxpy.gpx import GPXTrackPoint, GPXWaypoint
from math import isclose
from typing import TextIO, Union

WANT_DIST_M_DEFAULT = 2000
EQU_PNT_TOLERANCE_M=10
EQU_PNT_PNT_FN=lambda a, b: isclose(a.distance_2d(b), 0.0, rel_tol=0.0, abs_tol=EQU_PNT_TOLERANCE_M) # a: wpt_t, b: wpt_t, distance_2d(wpt_t)->meters

ROUND_DMS_SD_FN_DEFAULT=lambda sd: format(round(sd, ndigits=1), '04.1f')
ROUND_DMS_SD_FN_CUT=lambda sd: format(round(sd), '02.0f')

wpt_t = Union[GPXWaypoint, GPXTrackPoint]
vec_t = Union[wpt_t, list, tuple]

wpt_t_default = lambda p,v: GPXWaypoint(v[0], v[1], symbol='http://maps.me/placemarks/placemark-green.png', type='checkpoint')

formfeed = '\x0c'
n_formfeed = '\x0c\n'

class KoceDial(excel):
    def __init__(self):
        super().__init__()
        self.skipinitialspace = True

def DictReader(f: TextIO):
    nocomm = filter(lambda row: not len(row) or row[0] != '#', f)
    return DR(nocomm, dialect=KoceDial())
