from gpxpy.gpx import GPXWaypoint

if __name__ == '__main__':
    z1 = GPXWaypoint(46.36240955565504, 14.641876000045542)
    z2 = GPXWaypoint(46.360650035865056, 14.583001500831337)
    z3 = GPXWaypoint(46.37084281809474, 14.59281476243845)
    d1 = z1.distance_2d(z3)
    d2 = z2.distance_2d(z3)
    f = 1/1000 * 0.9
    print(d1, d2)
    print(d1 * f, d2 * f)
    print(z1.distance_2d(z2) * f)
    print(1000/9)