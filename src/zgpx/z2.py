from pathlib import Path
from typing import Callable, TypeVar

from gpxpy.gpx import GPXWaypoint
from zgpx.eform import eform, PriPage
from zgpx.util import ROUND_DMS_SD_FN_CUT, n_formfeed
from zgpx.ptutil import Pos, SYM_DIAMOND, chk_waypoints, chk_waypoints_insert_inplace, csv_waypoints, pnt_filter_closer_than, vec_t

import gpxpy

PICOS_WANT_DIST_M = 500
THIN_WANT_DIST_M = 500/3
NOTCLOSER_DIST_M = 0

root = Path('..').resolve()

def n2():
    with open(root / 'Slovenska_Planinska_Pot_Formatted.gpx', encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
        gp2.waypoints.extend(csv_waypoints(root / 'z0_koce.csv'))
        gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
        xm2 = gp2.to_xml()
        with open(root / 'zzz_generated_2.gpx', 'w', encoding='UTF-8') as f2:
            f2.write(xm2)

def n3():
    with open(root / 'Slovenska_Planinska_Pot_Formatted.gpx', encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)

    gp2.waypoints.extend(kwp := csv_waypoints(root / 'z0_koce.csv'))

    lstn = eform(gp2, kwp)

    with open(root / 'zzz_generated_5.txt', 'w', encoding='UTF-8') as f2:
        pp = PriPage(cponly=True)
        for x in lstn:
            pp.add_cure(x)
        f2.write(pp.output())

    outs = []
    for x in lstn:
        pp = PriPage(cponly=True)
        pp.add_cure(x)
        outs.append(pp.output())
    with open(root / 'zzz_generated_4.txt', 'w', encoding='UTF-8') as f2:
        f2.write(n_formfeed.join(outs))

    with open(root / 'zzz_generated_3.gpx', 'w', encoding='UTF-8') as f2:
        xm2 = gp2.to_xml()
        f2.write(xm2)

def n4():
    with open(root / 'el-anillo-de-picos-completo_formatted.gpx', encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(csv_waypoints(root / 'z2_koce.csv'))
    #gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
    with open(root / 'zzz_generated_el_2.gpx', 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

def n5():
    with open(root / 'el-anillo-de-picos-completo_formatted.gpx', encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(csv_waypoints(root / 'z2_landmark.csv'))
    #gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
    with open(root / 'zzz_generated_el_3.gpx', 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

def n6():
    with open(root / 'el-anillo-de-picos-completo_formatted.gpx', encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)

    landmark_wps = csv_waypoints(root / 'z2_landmark.csv')
    gp2.waypoints.extend(landmark_wps)

    chk_wps = pnt_filter_closer_than(chk_waypoints(gp2, want_dist_m=PICOS_WANT_DIST_M), gp2.waypoints, NOTCLOSER_DIST_M)
    chk_waypoints_insert_inplace(gp2, 'dummy_breaker', want_dist_m=PICOS_WANT_DIST_M)
    gp2.waypoints.extend(chk_wps)

    with open(root / 'zzz_generated_el_4.gpx', 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

def n7():
    with open(root / 'el-anillo-de-picos-completo_formatted.gpx', encoding='UTF-8') as f:
        gp2_thin = gpxpy.parse(f)
    gp2_thin.waypoints.extend(landmark_wps := csv_waypoints(root / 'z2_landmark.csv'))
    lst2 = eform(gp2_thin, gp2_thin.waypoints, want_dist_m=THIN_WANT_DIST_M)

    with open(root / 'el-anillo-de-picos-completo_formatted.gpx', encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(landmark_wps := csv_waypoints(root / 'z2_landmark.csv'))
    lstn = eform(gp2, gp2.waypoints, want_dist_m=PICOS_WANT_DIST_M)

    pp = PriPage(cponly=True, round_dms_sd_fn=ROUND_DMS_SD_FN_CUT)
    for x in lstn:
        pp.add_cure(x)
    with open(root / 'zzz_generated_el_5.txt', 'w', encoding='UTF-8') as f2:
        f2.write(pp.output())

    pp = PriPage(cponly=True, round_dms_sd_fn=ROUND_DMS_SD_FN_CUT)
    for x in lst2:
        pp.add_cure(x)
    with open(root / 'zzz_generated_el_6.txt', 'w', encoding='UTF-8') as f2:
        f2.write(pp.output())

    pp = PriPage(cponly=True, round_dms_sd_fn=ROUND_DMS_SD_FN_CUT, ncol=4, nrow=72)
    for x in lst2:
        pp.add_cure_thin(x, lstn)
    with open(root / 'zzz_generated_el_7.txt', 'w', encoding='UTF-8') as f2:
        f2.write(pp.output())

def n8():
    with open(root / 'Slovenska planinska pot_mapzs.gpx', encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
        gp2.waypoints.extend(csv_waypoints(root / 'z0_koce.csv'))

        def way_fact():
            seq = -1
            def _(p, v) -> Callable[[Pos, vec_t], TypeVar('T')]:
                nonlocal seq
                seq = seq + 1
                if seq % 3 == 0:
                    return GPXWaypoint(v[0], v[1], symbol=SYM_DIAMOND, name=f'{int(seq // 3)}', type='checkpoint')
                else:
                    return GPXWaypoint(v[0], v[1], symbol=SYM_DIAMOND, type='checkpoint')
            return _
        gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000/3.0, way_fact=way_fact()))

        xm2 = gp2.to_xml()
        with open(root / 'zzz_generated_8.gpx', 'w', encoding='UTF-8') as f2:
            f2.write(xm2)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--actn', default='n8')
    args = parser.parse_args()
    globals()[args.actn]()
