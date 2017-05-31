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
            att_factor = params.get("attenuate_factor", 0.5)
            attimg = attenuate_background(outimg, factor = att_factor)

            WHITE_DEBUG = params.get("white_debug", False)
            if WHITE_DEBUG:
                cv2.putText(attimg, "%d, %.2f" % (cur_whites, change_ratio), \
                        (0, abs(sub_h)-10), cv2.FONT_HERSHEY_PLAIN, 2.0, \
                        (0, 255, 255), 2)

            out_buffer.append(attimg)
    
        if len(out_buffer) == montage_height:
            out_image = np.concatenate(out_buffer, 0)
            cv2.imwrite(outdir + "/%04d.png" % out_counter, out_image)
            out_buffer = []
            out_counter += 1

    if len(out_buffer) > 0:
        out_image = np.concatenate(out_buffer, 0)
        cv2.imwrite(outdir + "/%04d.png" % out_counter, out_image)

def attenuate_background(img, factor = 0.5, params = {}):
    subtitle_color = params.get("subtitle_color", (230, 230, 230))
    ret_img = np.zeros(img.shape, dtype = np.uint8)
    att_img = np.uint8(img * factor)
    
    mask = np.ones(img.shape[0:2], dtype = np.uint8) * 255
    for col_i in range(3):
        _, mask_x = cv2.threshold(img[:,:,col_i], subtitle_color[col_i], 255,
                cv2.THRESH_BINARY)
        cv2.bitwise_and(mask, mask_x, mask)
    cv2.dilate(mask, 
        cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
        mask)
    mask_inv = cv2.bitwise_not(mask)
    # cv2.imshow('mask', mask); cv2.waitKey()

    for col_i in range(3):
        ori_img = img[:,:,col_i]
        sub_img = cv2.bitwise_and(ori_img, ori_img, mask = mask)
        att_x = att_img[:,:,col_i]
        att_bg = cv2.bitwise_and(att_x, att_x, mask = mask_inv)
        op_img = cv2.add(att_bg, sub_img)
        ret_img[:,:,col_i] = op_img

    return ret_img
