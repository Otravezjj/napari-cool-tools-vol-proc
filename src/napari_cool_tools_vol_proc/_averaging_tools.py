"""
This module contains code for loading .prof files wihout .xml metadata
"""
import numpy as np
from skimage.measure import block_reduce
from napari.utils.notifications import show_info
from napari.layers import Image, Layer
from napari.types import ImageData

def average_bscans(vol:Image, scans_per_avg:int=5) -> Layer:
    """Function to map image/B-scan values to a specific range between min_val and max_val.

    Args:
        vol (Image): vol representing volumetric or image stack data
        scans_per_avg (int): number of consecutive images/B-scans to average together

    Returns:
        Layer volume where values have been averaged every scans_per_avg images/B-scans along the depth dimension
    """
    data = vol.data
    name = f"{vol.name}_avg_5"
    add_kwargs = {"name":name}
    layer_type = "image"
    averaged_array = block_reduce(data, block_size=(scans_per_avg,1,1), func= np.mean)
    layer = Layer.create(averaged_array,add_kwargs,layer_type)

    return layer

def average_per_bscan(vol: Image, scans_per_avg: int = 5, axis = 0, trim: bool = True) -> Layer:
    """Accepts an n-dimesional array and an odd integer of scans to average together per b-scan
    and returns an n-dimensional array where each slice is an average of the surrounding
    bscans from the original array

    The array length may very slightly depending on how edge cases are handled
    
    vol = volume data
    
    scans_per_avg = number of b-scans to average together currently assumes an odd number"""

    data = vol.data
    name = f"{vol.name}_5_per"
    add_kwargs = {"name":name}
    layer_type = "image"
    
    if scans_per_avg % 2 == 1:
        offset = int((scans_per_avg - 1) / 2)

        print(f"shape: {data.shape}, axis: {axis}, length of axis {data.shape[axis]}")

        length = data.shape[axis]

        averaged_slices = []

        for i in range(length):
            if i >= offset and i < length - offset:
                print(f"Averaging slices...\nGenerating new slice by averaging slices {i-offset} through {i+offset} of {length-1}")
                
                if axis == 0:
                    start0 = i-offset
                    end0 = i+offset+1
                    start1 = 0
                    end1 = data.shape[1]
                    start2 = 0
                    end2 = data.shape[2]
                elif axis == 1:
                    start0 = 0
                    end0 = data.shape[0]
                    start1 = i-offset
                    end1 = i+offset+1
                    start2 = 0
                    end2 = data.shape[2]
                elif axis == 2:
                    start0 = 0
                    end0 = data.shape[0]
                    start1 = 0
                    end1 = data.shape[1]
                    start2 = i-offset
                    end2 = i+offset+1
                else:
                    print(f"You done effed up!!")

                averaged_slice = data[start0:end0,start1:end1,start2:end2].mean(axis)                
                
                #averaged_slice = data[i-offset:i+offset+1,:,:].mean(axis)
                averaged_slices.append(averaged_slice)
            else:
                if trim == False:
                    if i < offset:

                        if axis == 0:
                            start0 = i
                            end0 = i+1
                            start1 = 0
                            end1 = data.shape[1]
                            start2 = 0
                            end2 = data.shape[2]
                        elif axis == 1:
                            start0 = 0
                            end0 = data.shape[0]
                            start1 = i
                            end1 = i+1
                            start2 = 0
                            end2 = data.shape[2]
                        elif axis == 2:
                            start0 = 0
                            end0 = data.shape[0]
                            start1 = 0
                            end1 = data.shape[1]
                            start2 = i
                            end2 = i+1
                        else:
                            print(f"You done effed up!!")

                        averaged_slice = data[start0:end0,start1:end1,start2:end2].squeeze(axis)

                        averaged_slices.append(averaged_slice)    

                        pass

                    elif i >= length - offset:

                        if axis == 0:
                            start0 = i
                            end0 = i+1
                            start1 = 0
                            end1 = data.shape[1]
                            start2 = 0
                            end2 = data.shape[2]
                        elif axis == 1:
                            start0 = 0
                            end0 = data.shape[0]
                            start1 = i
                            end1 = i+1
                            start2 = 0
                            end2 = data.shape[2]
                        elif axis == 2:
                            start0 = 0
                            end0 = data.shape[0]
                            start1 = 0
                            end1 = data.shape[1]
                            start2 = i
                            end2 = i+1
                        else:
                            print(f"You done effed up!!")

                        averaged_slice = data[start0:end0,start1:end1,start2:end2].squeeze(axis)

                        averaged_slices.append(averaged_slice)  

                        pass
                else:
                    print(f"You shouldn't be here {average_per_bscan}!!")

        averaged_array = np.stack(averaged_slices, axis=axis)

        layer = Layer.create(averaged_array,add_kwargs,layer_type)

        return layer
    else:
        print(f"scans_per_avg should be an odd number please use an odd number for this value")
        show_info(f"scans_per_avg should be an odd number please use an odd number for this value")
        return data