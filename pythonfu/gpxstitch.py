#!/usr/bin/env python

# i0 = gimp.image_list()[0]

from gimpfu import *
import time

DirRoot = 'C:/Users/Andrej/test/snw/maps/picos/'
BufNam = 'gpxstitch_buffer'

def exc(*args):
    gimp.message('ERR: ' + str(args))
    raise RuntimeError(args)

def img_lay(img, idx):
    if len(img.layers) <= idx:
        exc('img_lay')
    return img.layers[idx]

def cp(img, lay):
    FileName = DirRoot + '0.png'
    i0 = pdb.gimp_file_load(FileName, FileName, run_mode=RUN_NONINTERACTIVE)
    l0 = img_lay(i0, 0)
    pdb.gimp_edit_named_copy(l0, BufNam)
    pdb.gimp_floating_sel_anchor(pdb.gimp_edit_named_paste(lay, BufNam, False))


def doit(img, lay):
    gimp.message('S : ' + str(time.time()))
    cp(img, lay)
    gimp.message(' E: ' + str(time.time()))

register('python_fu_gpxstitch', 'a', 'a', 'a', 'a', '2020', '<Image>/Filters/gpxstitch', '*', [], [], doit)

main()
