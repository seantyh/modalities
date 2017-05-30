import numpy as np
import pdb

def get_subtitle_threshold(data_vec):
    histy, histx = np.histogram(data_vec[data_vec > 0], 20)
    ysmooth = np.convolve(histy, [0.3,0.4,0.3], "same")
    ysmooth[0] = ysmooth[1]
    pos_diff = np.where(np.diff(ysmooth) > 0)

    if np.any(pos_diff):
        # if smoothed version can find a positive increment
        x_idx = histx[np.min(pos_diff)]
    else:
        try:
            x_idx = histx[np.min(np.where(np.diff(histy) > 0))]
        except Exception as ex: 
            # if there is still a problem finding one
            # just assign a value
            print("WARNING: Cannot find a threshold adaptively")
            x_idx = histx[1]
    return x_idx
