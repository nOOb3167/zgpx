# %APPDATA%/Roaming/GIMP/2.10/plug-ins/p0.py

from gimpfu import *
import gimpcolor

SZ = 800

def rte(): raise RuntimeError()

def copypaste(imgold, layold, imgnew, laynew, wh, xyold, xynew):
    pdb.gimp_image_select_rectangle(imgold, CHANNEL_OP_REPLACE, xyold[0], xyold[1], wh[0], wh[1])
    pdb.gimp_edit_copy(layold) or rte()
    pdb.gimp_image_select_rectangle(imgnew, CHANNEL_OP_REPLACE, xynew[0], xynew[1], wh[0], wh[1])
    pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(laynew, False))

def z0(img, layer):
    bas = img.layers[-1]

    layers = [
        pdb.gimp_layer_new(img, SZ, SZ, RGB_IMAGE, "base", 100, NORMAL_MODE),
        pdb.gimp_layer_new(img, SZ, SZ, RGB_IMAGE, "base", 100, NORMAL_MODE),
    ]
    for l in layers:
        pdb.gimp_layer_add_alpha(l)
        pdb.gimp_image_add_layer(img, l, 0)

    drw = pdb.gimp_image_get_active_drawable(img)
    pdb.gimp_context_set_background(gimpcolor.RGB(255, 0, 0))
    pdb.gimp_drawable_fill(drw, FILL_BACKGROUND)

    copypaste(img, drw, img, bas, [400, 400], [0, 0], [128, 128])

def stitchhorz(img, layer):
    iwh = [sum([l.width for l in img.layers]), max([l.height for l in img.layers])]
    img_new = pdb.gimp_image_new(iwh[0], iwh[1], RGB)
    lay_new = pdb.gimp_layer_new(img_new, iwh[0], iwh[1], RGB_IMAGE, 'base', 100, LAYER_MODE_NORMAL)
    pdb.gimp_layer_add_alpha(lay_new)
    pdb.gimp_image_add_layer(img_new, lay_new, 0)

    ll = img.layers; ll.reverse()
    wpos = iwh[0]
    for l in ll:
        wpos = wpos - l.width
        copypaste(img, l, img_new, lay_new, [l.width, l.height], [0, 0], [wpos, 0])

    pdb.gimp_display_new(img_new)

register("python_fu_z0", "", "", "", "", "", "<Image>/Filters/z0", "*", [], [], z0)
register("python_fu_stitchhorz", "", "", "", "", "", "<Image>/Filters/z0stitchhorz", "*", [], [], stitchhorz)
main()
