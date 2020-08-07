from pathlib import Path
from z1 import chk_waypoints, pnt_filter_closer_than
from z0 import chk_waypoints_insert_inplace, csv_waypoints

import gpxpy

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

    notcloser_dist_m = 100
    want_dist_m = 300

    chk_wps = pnt_filter_closer_than(chk_waypoints(gp2, want_dist_m=want_dist_m), gp2.waypoints, notcloser_dist_m)
    chk_waypoints_insert_inplace(gp2, 'dummy_breaker', want_dist_m=want_dist_m)
    gp2.waypoints.extend(chk_wps)

    with open(root.joinpath('zzz_generated_el_4.gpx'), 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

if __name__ == '__main__':
    n4()
    n5()
    n6()
