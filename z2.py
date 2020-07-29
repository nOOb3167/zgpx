from pathlib import Path
from z0 import csv_waypoints

import gpxpy

root = Path('.').resolve()

def n4():
    with open(root.joinpath('el-anillo-de-picos-completo_formatted.gpx'), encoding='UTF-8') as f:
        gp2 = gpxpy.parse(f)
    gp2.waypoints.extend(csv_waypoints(root.joinpath('z2_koce.csv')))
    #gp2.waypoints.extend(chk_waypoints(gp2, want_dist_m=1000))
    with open(root.joinpath('zzz_generated_el_2.gpx'), 'w', encoding='UTF-8') as f2:
        f2.write(gp2.to_xml())

if __name__ == '__main__':
    n4()
