"""
This module contains code for mainpulating volumetric data with label masks.
"""

import numpy as np
from math import sqrt
from napari.utils.notifications import show_info
from napari.qt.threading import thread_worker
from napari.layers import Image, Labels, Layer
from napari_cool_tools_io import viewer

def isolate_labeled_volume(vol:Image,label_vol:Labels,label:int)->Image:
    """"""
    isolate_labeled_volume_thread(vol=vol,label_vol=label_vol,label=label)

    return
    
@thread_worker(connect={"returned": viewer.add_layer})
def isolate_labeled_volume_thread(vol:Image,label_vol:Labels,label:int)->Image:
    """"""
    show_info(f"Isolate labeled volume thread started")
    layer = isolate_labeled_volume_func(vol=vol,label_vol=label_vol,label=label)
    show_info(f"Isolate labeled volume thread completed")

    return layer

def isolate_labeled_volume_func(vol:Image,label_vol:Labels,label:int)->Layer:
    """"""
    img_data = vol.data
    lbl_data = label_vol.data
    name = f"{vol.name}_{label}_mask"
    layer_type = 'image'
    add_kwargs = {"name":f"{name}"}

    label_mask = lbl_data == label
    out_vol = img_data.copy()
    out_vol[~label_mask] = 0
    layer = Layer.create(out_vol,add_kwargs,layer_type)

    return layer

def find_brightest_avg_pixels(vol:Image,pixels_to_avg:int=8,axis:int=1) -> Labels:
    ''''''
    data = vol.data
    

    reshape = data.reshape(-1,pixels_to_avg,data.shape[-1])
    reshape_avg = reshape.mean(1)

    viewer.add_image(reshape_avg)

    col_idx = reshape_avg.max(0).astype(np.uint8)
    row_idx = np.arange(reshape_avg.shape[1])

    print(col_idx,row_idx)

    bright_mask = np.zeros_like(reshape_avg,dtype=np.uint8)
    bright_mask[(col_idx,row_idx)] = 2

    print(col_idx,row_idx)
    viewer.add_labels(bright_mask)
    
