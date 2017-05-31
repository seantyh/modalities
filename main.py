
import os
import sys
from download_youtube import *
from find_threshold import *
from export_frames import *
from analyze_frames import *
from text_detection import *
from configparser import ConfigParser

def tp(instr):
    toks = instr[1:-1].split(",")
    return tuple(int(x) for x in toks)

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        config = ConfigParser()
        config.read(config_path)
    else:
        print("main.py <config file>")
        exit(-1)
    
    DOWNLOAD_VIDEO = config.getboolean("PROC", "DOWNLOAD_VIDEO")
    ANALYZE_IMAGE = config.getboolean("PROC", "ANALYZE_IMAGE")
    EXPORT_IMAGE = config.getboolean("PROC", "EXPORT_IMAGE")
    DETECT_TEXT = config.getboolean("PROC", "DETECT_TEXT")
    REVISE_TEXT = config.getboolean("PROC", "REVISE_TEXT")

    URL = config.get("FILE", "URL")
    VIDEO_PATH = config.get("FILE", "VIDEO_PATH")
    OUT_DIR = config.get("FILE", "OUT_DIR")
    prefix = os.path.basename(VIDEO_PATH).split(".")[0]
    DATA_PATH = os.path.join(OUT_DIR, "{}.npy".format(prefix))
    params = {"subtitle_color": tp(config.get("PARAMS", "subtitle_color")),
              "subtitle_height": config.getint("PARAMS", "subtitle_height"),
              "skip_seconds": config.getint("PARAMS", "skip_seconds"),
              "end_seconds": config.getint("PARAMS", "end_seconds"),
              "montage_height": config.getint("PARAMS", "montage_height"),
              "debug_plot": config.getboolean("PARAMS", "debug_plot"),
              "white_debug": config.getboolean("PARAMS", "white_debug"),
              "attenuate_factor": config.getfloat("PARAMS", "attenuate_factor")}
    
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        print("Create new directory " + OUT_DIR)

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
