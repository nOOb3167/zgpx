from pathlib import Path
from zgpx.z1 import chk_waypoints, pnt_filter_closer_than
from zgpx.z0 import PriPage, ROUND_DMS_SD_FN_CUT, chk_waypoints_insert_inplace, csv_waypoints, eform

import gpxpy

PICOS_WANT_DIST_M = 500
THIN_WANT_DIST_M = 500/3
NOTCLOSER_DIST_M = 0

root = Path('.').resolve()

def n4():
    with open(root.joinpath('el-anillo-de-picos-completo_formatted.gpx'), encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(csv_waypoints(root.joinpath('z2_koce.csv')))
    #gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
    with open(root.joinpath('zzz_generated_el_2.gpx'), 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

def n5():
    with open(root.joinpath('el-anillo-de-picos-completo_formatted.gpx'), encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(csv_waypoints(root.joinpath('z2_landmark.csv')))
    #gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
    with open(root.joinpath('zzz_generated_el_3.gpx'), 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

def n6():
    with open(root.joinpath('el-anillo-de-picos-completo_formatted.gpx'), encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)

    landmark_wps = csv_waypoints(root.joinpath('z2_landmark.csv'))
    gp2.waypoints.extend(landmark_wps)

    chk_wps = pnt_filter_closer_than(chk_waypoints(gp2, want_dist_m=PICOS_WANT_DIST_M), gp2.waypoints, NOTCLOSER_DIST_M)
    chk_waypoints_insert_inplace(gp2, 'dummy_breaker', want_dist_m=PICOS_WANT_DIST_M)
    gp2.waypoints.extend(chk_wps)

    with open(root.joinpath('zzz_generated_el_4.gpx'), 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

def n7():
    with open(root.joinpath('el-anillo-de-picos-completo_formatted.gpx'), encoding='UTF-8') as f:
        gp2_thin = gpxpy.parse(f)
    gp2_thin.waypoints.extend(landmark_wps := csv_waypoints(root.joinpath('z2_landmark.csv')))
    lst2 = eform(gp2_thin, gp2_thin.waypoints, want_dist_m=THIN_WANT_DIST_M)

    with open(root.joinpath('el-anillo-de-picos-completo_formatted.gpx'), encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(landmark_wps := csv_waypoints(root.joinpath('z2_landmark.csv')))
    lstn = eform(gp2, gp2.waypoints, want_dist_m=PICOS_WANT_DIST_M)

    pp = PriPage(cponly=True, round_dms_sd_fn=ROUND_DMS_SD_FN_CUT)
    for x in lstn:
        pp.add_cure(x)
    with open(root.joinpath('zzz_generated_el_5.txt'), 'w', encoding='UTF-8') as f2:
        f2.write(pp.output())

    pp = PriPage(cponly=True, round_dms_sd_fn=ROUND_DMS_SD_FN_CUT)
    for x in lst2:
        pp.add_cure(x)
    with open(root.joinpath('zzz_generated_el_6.txt'), 'w', encoding='UTF-8') as f2:
        f2.write(pp.output())

    pp = PriPage(cponly=True, round_dms_sd_fn=ROUND_DMS_SD_FN_CUT, ncol=4, nrow=72)
    for x in lst2:
        pp.add_cure_thin(x, lstn)
    with open(root.joinpath('zzz_generated_el_7.txt'), 'w', encoding='UTF-8') as f2:
        f2.write(pp.output())

if __name__ == '__main__':
    #n4()
    #n5()
    #n6()
    n7()
