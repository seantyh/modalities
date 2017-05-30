from google.cloud import vision
import os
import json
import pdb
import re
import glob

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
        "E:\\keys\\KyleBlackbox-424c3a405db3.json"
chpat = re.compile("[\u4e00-\u9fff\uf900-\ufaff\uf900-\ufaff]")
def detect_text(outdir, prefix):
    txtObj = {}
    png_files = glob.glob(outdir + "/*.png")
    for i, imgpath in enumerate(png_files):
        if not imgpath.endswith(".png"): continue
        print("text detection: %s [%d%%]" % \
                (imgpath, i / len(png_files) * 100))
        texts = google_detect_text(os.path.join(outdir, imgpath))
        if len(texts) == 0: continue
        try:
            img_key = os.path.basename(imgpath)
            img_idx = int(img_key.replace(".png", ""))
        except ValueError:
            img_idx = imgpath
        txtObj[img_idx] = texts[0].description
        # if imgpath == "0002.png": break

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

    texts = image.detect_text()

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
    
    sorted_keys = sorted(jObj.keys(), key = lambda x: int(x))
    content = "\n".join([jObj.get(k) for k in sorted_keys])
    lines = content.split("\n")
    prev_ln = []
    buf = []
    for ln in lines:
        if len(prev_ln) > 5: prev_ln = prev_ln[1:]
        if len(ln) <= 1: 
            continue
        
        if ln not in prev_ln and len(chpat.findall(ln)) / len(ln) > 0.8:                     
            buf.append(ln)            
            prev_ln.append(ln)
    
    open(json_path.replace(".json", ".txt"), "w", encoding="UTF-8")\
         .write("\n".join(buf))
