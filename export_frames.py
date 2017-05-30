import cv2
import numpy as np
import pdb

def export_subtitles(video_path, outdir, data_vec, 
        thres, change_thres = 1.5, params = {}):
    cap = cv2.VideoCapture(video_path)
    n_frame = data_vec.shape[0]
    prev_whites = 0
    frame_counter = -1
    out_counter = 0
    montage_height = params.get("montage_height", 10)
    
    out_buffer = []
    while(cap.isOpened()):
        frame_counter += 1
        
        if frame_counter >= n_frame: break
        ret, frame = cap.read()
        if not ret: break
        
        if frame_counter % 1000 == 0:
            print("Extracting: %d [%d%%]" % \
                    (frame_counter, \
                     frame_counter / n_frame * 100))

        cur_whites = np.int32(data_vec[frame_counter])
        prev_whites = data_vec[frame_counter - 1]
        
        sub_h = params.get("subtitle_height", -100)
        if prev_whites > 0:
            change_ratio = np.abs(cur_whites - prev_whites) / prev_whites
        else:
            change_ratio = change_thres + 0.1

        if cur_whites > thres and change_ratio > change_thres:
            # print("cur: %d, prev: %d, chg: %.2f" % \
            #         (cur_whites, prev_whites, change_ratio))
            prev_whites = cur_whites
            outimg = frame[sub_h:,:,:]

            WHITE_DEBUG = params.get("white_debug", False)
            if WHITE_DEBUG:
                cv2.putText(outimg, "%d, %.2f" % (cur_whites, change_ratio), \
                        (0, 90), cv2.FONT_HERSHEY_PLAIN, 2.0, \
                        (255, 0, 0), 2)

            out_buffer.append(outimg)
    
        if len(out_buffer) == montage_height:
            out_image = np.concatenate(out_buffer, 0)
            cv2.imwrite(outdir + "/%04d.png" % out_counter, out_image)
            out_buffer = []
            out_counter += 1

    if len(out_buffer) > 0:
        out_image = np.concatenate(out_buffer, 1)
        cv2.imwrite(outdir + "/%04d.png" % out_counter, out_image)

