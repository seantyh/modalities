
import ssl
from pytube import YouTube
ssl._create_default_https_context = ssl._create_unverified_context

def get_youtube(url, outpath):

    yt = YouTube(url)    
    vid = yt.get('mp4', '360p')
    if vid is None:
        print(yt.get_videos())
        spec = input("Input spec (e.g. mp4, 340p): ")
        toks = spec.split(',')
        vid = yt.get(toks[0].strip(), toks[1].strip())
    print("Downloading to {}".format(outpath))
    vid.download(outpath)
        
    
