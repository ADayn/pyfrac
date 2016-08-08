#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Mohit Sharma
# Aug 08 2016
# NYU CUSP 2016
"""
Converting CSV files to JPG for displaying on
website.
"""

from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import os
from pyfrac.utils import pyfraclogger
from pyfrac.utils.misc import ignored

logger = pyfraclogger.pyfraclogger(tofile=True)


def tojpg(csvfile, patchfile):
    """
    Convert the csv file to jpg
    Parameters
    ----------
    csvfile: str
        CSV file path

    patchfile: str
        File containing pixel locations for
        rectangular "patch" whose average temp
        is to be calculated.
        It should be in following format
          TAG:1
          x
          y
          x1
          y1
          ...
          TAG:N
          x
          y
          x1
          y1

    Returns
    -------
    jpgfile: str
        JPG file path
    """

    patch = None
    with open(patchfile, "r") as pf:
        patch = pf.read()

    img = np.loadtxt(csvfile, delimiter=",")

    tags = re.findall('(TAG:[\d]+)([\n\d]+)+', patch)
    rectangles = {}
    for tag in tags:
        coords = tag[1].strip('\n').splitlines()
        coords = map(lambda x: int(x) / 2, coords)
        avg_temp = img[coords[0]: coords[2], coords[1]: coords[3]].mean()
        rectangles.update({tag[0] + "- %.2f degC " % avg_temp: patches.Rectangle(
            (coords[0], coords[1]),
            coords[2] - coords[0],
            coords[3] - coords[1],
            hatch='',
            fill=False)
        })

    fig = plt.figure()
    ax1 = fig.add_subplot(111, aspect="equal")
    cax = ax1.imshow(img, cmap="nipy_spectral")
    cbar = fig.colorbar(cax, ticks=[img.min(), img.max()])

    for rects in rectangles:
        ax1.add_patch(rectangles[rects])
        rx, ry = rectangles[rects].get_xy()
        cx = rx + rectangles[rects].get_width()
        cy = ry + rectangles[rects].get_height()

        ax1.annotate(rects, (cx, cy), color='k', weight='bold',
                     fontsize=10, ha='left', va='bottom')

    fig.savefig(os.path.join(os.path.expanduser("~/Pictures"),
                             os.path.basename(csvfile)[:-3] + "png"))
