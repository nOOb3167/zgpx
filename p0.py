# %APPDATA%/Roaming/GIMP/2.10/plug-ins/p0.py

from gimpfu import *
import gimpcolor

SZ = 800

def rte(): raise RuntimeError()

def copypaste(img, layold, laynew, wh, xyold, xynew):
    pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE, xyold[0], xyold[1], wh[0], wh[1])
    pdb.gimp_edit_copy(layold) or rte()
    pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE, xynew[0], xynew[1], wh[0], wh[1])
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

    copypaste(img, drw, bas, [400, 400], [0, 0], [128, 128])

register(
    "python_fu_z0", "", "", "", "", "", "<Image>/Filters/z0", "*",
    #[(PF_STRING, "message", "Message to display", "hello")],
    [],
    [], z0)
main()
