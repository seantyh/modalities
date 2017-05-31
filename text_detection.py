from google.cloud import vision
import os
import json
import pdb
import re
import glob

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
        "E:\\keys\\KyleBlackbox-424c3a405db3.json"
chpat = re.compile("[\u4e00-\u9fff\uf900-\ufaff\uf900-\ufaff]")
chpat_head = re.compile("^[^\u4e00-\u9fff\uf900-\ufaff\uf900-\ufaff]+")
chpat_tail = re.compile("[^\u4e00-\u9fff\uf900-\ufaff\uf900-\ufaff]+$")

def detect_text(outdir, prefix):
    txtObj = {}
    png_files = glob.glob(outdir + "/*.png")
    for i, imgpath in enumerate(png_files):
        if not imgpath.endswith(".png"): continue
        print("text detection: %s [%02d%%]" % \
                (imgpath, i / len(png_files) * 100))
        texts = google_detect_text(os.path.join(outdir, imgpath))
        if len(texts) == 0: continue
        try:
            img_key = os.path.basename(imgpath)
            img_idx = int(img_key.replace(".png", ""))
        except ValueError:
            img_idx = imgpath
        txtObj[img_idx] = texts[0].description
        # if img_key == "0002.png": break

    fout = open(os.path.join(outdir, "text_detect_%s.json" % prefix), 
            "w", encoding="UTF-8")
    json.dump(txtObj, fout, indent=2, ensure_ascii = False)
    fout.close()

def google_detect_text(imgpath):
    """Detects text in the file."""
    vision_client = vision.Client()
    
    with open(imgpath, 'rb') as image_file:
        content = image_file.read()

    image = vision_client.image(content=content)

    texts = image.detect_text(100)
    return texts

def print_text(texts):
    print('Texts:')
    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(bound.x_coordinate, bound.y_coordinate)
                    for bound in text.bounds.vertices])

        print('bounds: {}'.format(','.join(vertices)))


def revise_text(json_path):
    fin = open(json_path, "r", encoding="UTF-8")
    jObj = json.load(fin)
    
    fout = open(json_path.replace(".json", ".txt"), "w", encoding="UTF-8")
    sorted_keys = sorted(jObj.keys(), key = lambda x: int(x))
    prev_ln = []
    for k in sorted_keys:
        fout.write("# extracted montage: %s\n" % k)
        lines = jObj[k].split("\n")
        for ln in lines:
            if len(prev_ln) > 5: prev_ln = prev_ln[1:]
            if len(ln) <= 1: 
                continue
            
            san_ln = strip_non_zh(ln)
            if len(san_ln) == 0: continue

            # comute min_distance between ln and all prev_ln's
            if len(prev_ln) > 0:
                min_dist = min([levenshtein(san_ln, prev_ln_x) \
                                for prev_ln_x in prev_ln])
            else:
                min_dist = 10

            if min_dist > 2 and len(chpat.findall(san_ln)) / len(san_ln) > 0.8:                                 
                fout.write(san_ln + "\n")
                prev_ln.append(san_ln)

def strip_non_zh(inputs):
    ret = chpat_head.sub("", inputs)
    ret = chpat_tail.sub("", ret)
    return ret

# copy from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]
    
