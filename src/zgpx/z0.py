from dataclasses import dataclass
from pathlib import Path

import gpxpy
from gpxpy.gpx import GPX, GPXTrackPoint, GPXWaypoint
from zgpx.eform import PriPage, eform
from zgpx.ptutil import (EQU_PNT_PNT_FN, chk_waypoints, dd2dms, gpx_insert_lseg_closest_inplace, mkpt, Pos, tra_seg,
    vec_isclose, vec_t, WANT_DIST_M_DEFAULT, wpt_t)
from zgpx.util import DictReader, n_formfeed


assert mkpt('46.5017784 15.5537548').latitude == GPXTrackPoint(46.5017784, 15.5537548).latitude and \
    mkpt('46.5017784 15.5537548').longitude == GPXTrackPoint(46.5017784, 15.5537548).longitude

root = Path('.').resolve()

def csv_waypoints(p: Path, t='trasa'):
    with open(p, encoding='UTF-8') as f:
        return [GPXWaypoint(latitude=float(r['latitude']), longitude=float(r['longitude']), name=r['name'], symbol='http://maps.me/placemarks/placemark-red.png', type=t) for r in DictReader(f)]

def koce_waypoints():
    return csv_waypoints(root / 'z0_koce.csv')

def vode_waypoints():
    with open(root / 'z SPP Voda.gpx', encoding='UTF-8') as f:
        return [x for x in gpxpy.parse(f).waypoints]

with open(root / 'Slovenska_Planinska_Pot_Formatted.gpx', encoding='UTF-8') as f:
    gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(koce_waypoints())
    gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
    xm2 = gp2.to_xml()
    with open(root / 'zzz_generated_2.gpx', 'w', encoding='UTF-8') as f2:
        f2.write(xm2)

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
