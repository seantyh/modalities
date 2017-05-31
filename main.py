
import os
from download_youtube import *
from find_threshold import *
from export_frames import *
from analyze_frames import *
from text_detection import *

DOWNLOAD_VIDEO = False
ANALYZE_IMAGE = False
EXPORT_IMAGE = False
DETECT_TEXT = False
REVISE_TEXT = True

if __name__ == "__main__":
    
    URL = "https://www.youtube.com/watch?v=i7gmio4w_sk"
    VIDEO_PATH = "h:/supertaste_20170504.mp4"
    OUT_DIR = "h:/supertaste_20170504"    
    prefix = os.path.basename(VIDEO_PATH).split(".")[0]
    DATA_PATH = os.path.join(OUT_DIR, "{}.npy".format(prefix))
    params = {"subtitle_color": (230, 230, 230),
              "subtitle_height": -80,
              "skip_frames": 340 * 30,
              "end_frames": -1,
              "motage_height": 10,
              "debug_plot": True,
              "white_debug": True}

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        print("Create new directory " + OUT_DIR)
    else:
        pass
        # list(os.remove(OUT_DIR + "/" + x) for x in os.listdir(OUT_DIR))
        # print("Reset contents in " + OUT_DIR)

    if DOWNLOAD_VIDEO:
        get_youtube(URL, VIDEO_PATH)
        
    if ANALYZE_IMAGE:
        white_vec = analyze_whites(VIDEO_PATH, params)
        np.save(DATA_PATH, white_vec)
    
    if EXPORT_IMAGE:
        white_vec = np.load(DATA_PATH)
        sub_thres = get_subtitle_threshold(white_vec)
        print("Subtitle threshold: " + str(sub_thres))
        export_subtitles(VIDEO_PATH, OUT_DIR, white_vec, 
                sub_thres, change_thres = 0.5, params = params)
    
    if DETECT_TEXT:
        detect_text(OUT_DIR, prefix)
    
    if REVISE_TEXT:
        revise_text(os.path.join(OUT_DIR, "text_detect_%s.json" % prefix))
