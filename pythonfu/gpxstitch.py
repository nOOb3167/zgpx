#!/usr/bin/env python

# https://www.gimp.org/docs/python/index.html

# http://gimpchat.com/viewtopic.php?f=9&t=5709
#   None vs 0 in API functions

# gimp_image_insert_layer: The layer type must be compatible with the image base type
#   fff = pdb.gimp_layer_new(img, enufw, enufh, RGBA_IMAGE, 'dummy', 100, LAYER_MODE_NORMAL)

# i0 = gimp.image_list()[0]

from gimpfu import *
import os, re, time

DirRoot = 'C:/Users/Andrej/test/snw/maps/picos/'

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
    pdb.gimp_edit_copy(lay)

def pas(img, lay, x, y, w, h):
    sel(img, x, y, w, h)
    pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(lay, True))

def addlayer(img, w, h):
    lay = pdb.gimp_layer_new(img, w, h, RGB_IMAGE, 'dummy', 100, LAYER_MODE_NORMAL)
    pdb.gimp_image_insert_layer(img, lay, None, -1)
    return lay

def sorted_png_fnam(dir):
    def fnam_sort(l):
        def tryint(s):
            try:
                return int(s)
            except:
                return s
        def key(s):
            return [tryint(s) for s in re.split('([0-9]+)', s)]
        return sorted(l, key=key)
    fnam = [f for f in os.listdir(dir)]
    return fnam_sort(filter(lambda x: re.match('.*\\.png$', x), fnam))

def pairwise(img, dir):
    fnam = sorted_png_fnam(dir)
    imgs = [pdb.gimp_file_load(DirRoot + fn, DirRoot + fn, run_mode=RUN_NONINTERACTIVE) for fn in fnam]
    enufw = max([img_lay(x, 0).width for x in imgs])
    enufh = max([img_lay(x, 0).height for x in imgs]) * 2
    fff = addlayer(img, enufw, enufh)
    for ix, i0 in enumerate(imgs):
        l0 = img_lay(i0, 0)
        cop(l0)
        pas(img, fff, 32, 32+ix*128, 128, 128)

def doit(img, lay):
    pairwise(img, DirRoot)

def doit_(img, lay):
    gimp.message('S : ' + str(time.time()))
    doit(img, lay)
    gimp.message(' E: ' + str(time.time()))

register('python_fu_gpxstitch', 'a', 'a', 'a', 'a', '2020', '<Image>/Filters/gpxstitch', '*', [], [], doit_)

main()
