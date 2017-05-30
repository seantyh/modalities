import numpy as np
import matplotlib.pyplot as plt
import cv2
import pdb

def analyze_whites(video_path, params = {}):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frame = params.get("end_frames", -1)
    if n_frame < 0:
        n_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    print("Analyzing whites")
    print("fps: %.2f, use %d frames" % (fps, n_frame))
    frame_counter = -1    

    white_vec = np.zeros(int(n_frame), dtype = np.uint32)
    stateObj = 0
    frame_history = []
    skip_frames = params.get("skip_frames", 0)

    while(cap.isOpened()):
        frame_counter += 1
        # print(frame_counter)
        ret, frame = cap.read()
        if frame_counter < skip_frames: continue
        # if frame_counter > 4000: break
        if ret is False: break

        if frame_counter >= n_frame: break

        if frame_counter % 1000 == 0:
            print("Analyzing frame: %d [%d%%]" % \
                    (frame_counter, \
                     frame_counter / n_frame * 100))
        cur_white = extract_frame(frame, frame_history, params)
        if len(frame_history) > 10:
            frame_history = frame_history[1:]
        
        try: 
            prev_white = white_vec[frame_counter - 1]
            white_vec[frame_counter] = cur_white        
        except IndexError as ex:
            pass
        
    return white_vec


def extract_frame(frame, history, params):
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except Exception as ex:
        print(ex)
        return 0
    
    sub_h = params.get("subtitle_height", -100)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize = 1)
    sobelx[sobelx < 0] = 0
    sobelx = np.uint8(sobelx)
    
    sub_color = params.get("subtitle_color", (250, 250, 250))
    _, high_B = cv2.threshold(frame[:,:,0], sub_color[2], 255, cv2.THRESH_BINARY)
    _, high_G = cv2.threshold(frame[:,:,1], sub_color[1], 255, cv2.THRESH_BINARY)
    _, high_R = cv2.threshold(frame[:,:,2], sub_color[0], 255, cv2.THRESH_BINARY)

    high_B[:sub_h, :] = 0
    high_BG = cv2.bitwise_and(high_B, high_G)
    high_BGR = cv2.bitwise_and(high_BG, high_R, high_BG)
    high_BGR = cv2.bitwise_and(high_BGR, sobelx, high_BGR)
    
    history.append(high_BGR)
    if len(history) > 10:
        # longitudinal BGR is a high_BGR intersect with history high_BGRs
        long_BGR = cv2.bitwise_and(high_BGR, history[0])
        long_BGR = cv2.bitwise_and(long_BGR, history[5], long_BGR)
        # print(np.sum(high_BGR - long_BGR != 0))
    else:
        long_BGR = high_BGR

    # if there is indeed subtitle, do further processing
    # cv2.erode(high_BGR, st_elem, high_BGR)
    n_whites = np.sum(long_BGR[sub_h:,:], 1)    
    hist_y, hist_x = np.histogram(n_whites)
    diff_lines = np.diff(hist_y)
    m_white = np.mean(np.percentile(n_whites, [90,95,99]))

    DEBUG_PLOT = params.get("debug_plot", False) and len(history) > 10
    if DEBUG_PLOT:        
        plt.subplot(3, 2, 1)
        plt.imshow(np.flip(frame, 2))
        plt.subplot(3, 2, 2)
        plt.imshow(long_BGR, cmap='gray')
        plt.subplot(3, 1, 2)    
        ax = plt.bar(hist_x[1:], hist_y, 
                     width = np.diff(hist_x)[0]/2,
                     align = "center")
        plt.text(hist_x[0], np.max(hist_y), "%.2f" % m_white,
                horizontalalignment='left',
                verticalalignment='top')
        plt.subplot(3, 1, 3)    
        ax = plt.plot(hist_x[1:], np.concatenate([[0], diff_lines]))
        plt.show()
        plt.close()
    
    return m_white

