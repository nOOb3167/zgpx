#!/usr/bin/env python

# https://www.gimp.org/docs/python/index.html

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

def sel(img, x, y, w, h):
    pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE, x, y, w, h)

def cop(lay):
    pdb.gimp_edit_named_copy(lay, BufNam)

def pas(img, lay, x, y, w, h):
    sel(img, x, y, w, h)
    pdb.gimp_floating_sel_anchor(pdb.gimp_edit_named_paste(lay, BufNam, True))

def doit(img, lay):
    FileName = DirRoot + '0.png'
    i0 = pdb.gimp_file_load(FileName, FileName, run_mode=RUN_NONINTERACTIVE)
    l0 = img_lay(i0, 0)
    cop(l0)
    pas(img, lay, 32, 32, 128, 128)

def doit_(img, lay):
    gimp.message('S : ' + str(time.time()))
    doit(img, lay)
    gimp.message(' E: ' + str(time.time()))

register('python_fu_gpxstitch', 'a', 'a', 'a', 'a', '2020', '<Image>/Filters/gpxstitch', '*', [], [], doit_)

main()
