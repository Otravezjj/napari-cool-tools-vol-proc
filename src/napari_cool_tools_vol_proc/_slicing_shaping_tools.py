'''Tools for slicing and reshaping multidimensional data'''

import numpy as np
from tqdm import tqdm
from napari.utils.notifications import show_info, show_warning
from napari.layers import Image, Layer
from napari.types import LayerDataTuple
from napari.qt.threading import thread_worker
from napari_cool_tools_io import viewer

def reshape_vol(vol:Image, new_shape:str="(-1,3,:,:)",debug:bool=False) -> Layer:
    """Function allowing reshaping of image data array Specifically intended for 
    reshaping OCTA data to represent individual m-scans in a separate dimension.
    Input the new data shape as a string in parenthases indicating the new dimensions
    of the volume. Use '-1' to indicate a single dimension to be autofilled. Use ':' 
    to indicate using the current dimensions along the given axis. This function
    is an implementation of numpy.reshape()/ndarray.reshape().

    To reshape an OCTA volume with integer n m-scans you would enter '-1,n,:,:'

    Args:
        vol (Image): vol representing volumetric or image stack data
        new_shape (string): new shape used to reshape the volume data

    Returns:
        Layer volume reshaped to fit shape

    Errors:
        Will fail if total number of data points are not divisible by the dimensions of
        the new shape data.

        All input must consist of charaters "():,-0123456789" or space
    """

    reshape_vol_thread(vol=vol,new_shape=new_shape,debug=debug)
    
    return

@thread_worker(connect={"returned": viewer.add_layer})
def reshape_vol_thread(vol:Image, new_shape:str="(-1,3,:,:)",debug:bool=False) -> Layer:
    """Function allowing reshaping of image data array Specifically intended for 
    reshaping OCTA data to represent individual m-scans in a separate dimension.
    Input the new data shape as a string in parenthases indicating the new dimensions
    of the volume. Use '-1' to indicate a single dimension to be autofilled. Use ':' 
    to indicate using the current dimensions along the given axis. This function
    is an implementation of numpy.reshape()/ndarray.reshape().

    To reshape an OCTA volume with integer n m-scans you would enter '-1,n,:,:'

    Args:
        vol (Image): vol representing volumetric or image stack data
        new_shape (string): new shape used to reshape the volume data

    Returns:
        Layer volume reshaped to fit shape

    Errors:
        Will fail if total number of data points are not divisible by the dimensions of
        the new shape data.

        All input must consist of charaters "():,-0123456789" or space
    """

    show_info(f'Reshape volume thread has started')
    layer = reshape_vol_func(vol=vol,new_shape=new_shape,debug=debug)
    show_info(f'Reshape volume thread has completed')

    return layer

def reshape_vol_func(vol:Image, new_shape:str="(-1,3,:,:)",debug:bool=False) -> Layer:
    """Function allowing reshaping of image data array Specifically intended for 
    reshaping OCTA data to represent individual m-scans in a separate dimension.
    Input the new data shape as a string in parenthases indicating the new dimensions
    of the volume. Use '-1' to indicate a single dimension to be autofilled. Use ':' 
    to indicate using the current dimensions along the given axis. This function
    is an implementation of numpy.reshape()/ndarray.reshape().

    To reshape an OCTA volume with integer n m-scans you would enter '-1,n,:,:'

    Args:
        vol (Image): vol representing volumetric or image stack data
        new_shape (string): new shape used to reshape the volume data

    Returns:
        Layer volume reshaped to fit shape

    Errors:
        Will fail if total number of data points are not divisible by the dimensions of
        the new shape data.

        All input must consist of charaters "():,-0123456789" or space
    """
    data = vol.data
    shape = data.shape
    if debug:
        show_info(f"New shape: {new_shape} of type {type(new_shape)}\n")
    else:
        pass

    new_shape = new_shape.strip()
    new_shape = new_shape.replace(" ","")
    if new_shape.startswith('(') and new_shape.endswith(')'):
        new_shape = new_shape.strip("()")
        new_dims = new_shape.split(",")

        if debug:
            show_info(f"New dimensions: {new_dims}\n")
        else:
            pass

    else:
        show_info("Invalid input for reshape_vol function.\nInput should be comma separated list of +integers, -1, or ':'s spaces are allowed.'")

    out_shape = []
    # case new shape longer than old shape
    if len(new_dims) > len(shape):
        # traverse existing shape and input existing values for any : found
        for i in range(len(new_dims)):
            j = (i+1)*-1
            #print(i,j)
            if i < len(shape):
                if new_dims[j] == ':':
                    out_shape.append(shape[j])
                else:
                    out_shape.append(int(new_dims[j]))
            else:
                out_shape.append(int(new_dims[j]))

        #show_info(f"outshape: {out_shape}\nout shape flip: {out_shape[::-1]}\n")
        out_shape = out_shape[::-1]

    # case new shape shorter than old shape
    elif len(shape) > len(new_dims):
        show_info(f"Not Yet Implemented")
    # case new shape same length as old shape
    else:
        show_info(f"Not Yet Implemented")
    
    reshaped = data.reshape(out_shape)

    name = f"{vol.name}_RS"
    add_kwargs = {"name":name}
    layer_type = "image"
    layer = Layer.create(reshaped,add_kwargs,layer_type)

    return layer

def split_vol(vol:Image, subvolumes:int=3, axis:int=1, debug:bool=False) -> LayerDataTuple:
    """Function splits volumes into subvolumes along the specified axis

    Args:
        vol (Image): vol representing volumetric or image stack data
        subvolumes (int): number of subvolumes to split manin volume into
        axis (int): axis along which to split the volume into subvolumes

    Returns:
        Subvolumes # Layers containing the subvolume layer data
    """

    data = vol.data
    shape = data.shape
    layers_out = []

    # calc step
    i_step = int(data.shape[axis]/subvolumes)

    # check that volume along axis is divisible by subvolumes
    if data.shape[axis]%subvolumes == 0:
        show_info(f"Axis {axis} is divisble by {subvolumes}\nAxis {axis} will be split into {subvolumes} x {i_step} chunks.")
    else:            
        show_warning(f"Axis {axis} is not divisble by {subvolumes}\nAxis {axis} will be split into {subvolumes} x {i_step} chunks.\n{data.shape[axis] - (subvolumes*i_step)} units along this dimenison will be lost\n")

    for i in range(subvolumes):

        # calc indicies
        i_start = (i*i_step)*(1-0**(i_step-1))+i

        # get slices
        slices = []

        for j in range(len(shape)):
            if j == axis:
                slices.append(slice(i_start,i_start+i_step))
            else:
                slices.append(slice(0,shape[j],1))

        if debug:
            show_info(f"slices: {slices}\n")
            show_info(f"Subvolume shape: {data[tuple(slices)].shape}\n")
        else:
            pass
        #print(f"data: {data[tuple(slices)]}\n")

        name = f"{vol.name}_{i}"
        #name = {i}
        add_kwargs = {"name":name}
        layer_type = "image"
        out = data[tuple(slices)].squeeze() # squeeze to eliminate axis eliminated by process
        #layer = Layer.create(data[tuple(slices)],add_kwargs,layer_type)
        layer_data_tuple = (out,add_kwargs,layer_type)

        #layers_out.append(layer)
        layers_out.append(layer_data_tuple)
    
    return layers_out

def stack_selected(axis:int=0, debug:bool=False)->Layer:
    """"""
    current_selection = list(viewer.layers.selection)
    data_stack = []
    
    for layer in current_selection:
        data_stack.append(layer.data)

    out_data = np.stack(data_stack,axis)
    name = f"Stacked_Selection_Axis_{axis}"
    add_kwargs = {"name": f"{name}"}
    layer_type = current_selection[0].as_layer_data_tuple()[2]
    layer = Layer.create(out_data,add_kwargs,layer_type)
    
    return layer   