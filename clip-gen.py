#!/usr/bin/env python3

import os
import re

import download
import uuid
import ffmpeg
import numpy as np
import cv2
import multiprocessing
from batch_face import RetinaFace
from tqdm import tqdm

from utils import check_directory, get_videos
from config import ROOT_DIR, DATASET_PATH, FACES_PATH, RESULTS_PATH
from random import randint
from datetime import datetime, timedelta



def init_worker():
    print('Creating networks and loading parameters')
    global face_detector
    face_detector = RetinaFace()


def video_face_cropper(dataset):
    global face_detector, processed_videos

    # Loop on videos in dataset
    for video in tqdm(dataset):

        random_frames = np.random.randint(1, 199, 10)
        frame_no = 0

        cap = cv2.VideoCapture(video)
        cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 0)

        while cap.isOpened():
            frame_no += 1

            # remove tmp if exist
            os.system(f"rm -rf /tmp/tmp*")

            ret, frame = cap.read()
            if ret:
                # Get random frame
                if frame_no in random_frames:

                    # Face detection
                    
                    face = face_detector(frame, cv=True)
                    """
                    if len(face) > 1:
                        # print("!! Two face detected!")
                        continue
                    """    
                    if len(face) == 1:
                        # print("!! NO face is detected!")
                        box, landmarks, confidence = face[0]

                        # Add Margin
                        (x, y, x2, y2) = box
                        margin = int(0.3 * (x2 - x))
                        x = max(x - margin, 0)
                        x2 = min(x2 + margin, frame.shape[1])
                        y = max(y - margin, 0)
                        y2 = min(y2 + margin, frame.shape[0])

                        # Save cropped video with sound
                        stream = ffmpeg.input(video)
                        file_name = f"{ROOT_DIR}/{FACES_PATH}/{uuid.uuid1()}.mp4"
                        ffmpeg.crop(stream, x, y, x2 - x, y2 - y).output(stream.audio, file_name,
                                                                        s="%sx%s" % (600, 500)).run()

                    """
                    command = f"ffmpeg -i {video} -filter_complex '[0:v]split=2[blur][vid];[" \
                              f"blur]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080," \
                              f"boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\," \
                              f"ch)/20:chroma_power=1[bg];[vid]scale=1080:1080:force_original_aspect_ratio=decrease[" \
                              f"ov];[bg][ov]overlay=(W-w)/2:(H-h)/1.6' /tmp/tmp.mp4 "
                    os.system(command)

                    command = f"ffmpeg -i /tmp/tmp.mp4 -filter:v 'crop=9/16*ih:ih' /tmp/tmp2.mp4"
                    os.system(command)
                    """
                    ###make tmp2
                    command = f"ffmpeg -crop 0x0x420x420 -c:v h264_cuvid -i {video} -c:a copy -c:v h264_nvenc -b:v 5M /tmp/tmp_square.mp4" #makes square
                    os.system(command)

                    start_sec = randint(0,14000)
                    yt_start=(timedelta(seconds=start_sec))

                    #command = f"ffmpeg -i file:/root/TwitchClip2Vertical/background.mp4 -ss {yt_start} -t 90 -filter:v \"crop=540:420,scale=1080:840\" -c:a copy /tmp/tmp_back.mp4"# makkes background
                    #os.system(command)

                    command = f"ffmpeg -c:v h264_cuvid -i /root/TwitchClip2Vertical/background.mp4 -ss {yt_start} -t 90 -c:a copy -c:v h264_nvenc -b:v 5M /tmp/tmp_back1.mp4"# makkes background
                    os.system(command)

                    command = f"ffmpeg -c:v h264_cuvid -crop 150x150x370x370 -resize 1080x840 -i /tmp/tmp_back1.mp4 -c:a copy -c:v h264_nvenc -b:v 5M /tmp/tmp_back.mp4"# makkes background
                    os.system(command)

                    command = f"ffmpeg -c:v h264_cuvid -i /tmp/tmp_square.mp4 -c:v h264_cuvid -i /tmp/tmp_back.mp4 -vsync 2 -filter_complex vstack -map 0:a -c:v h264_nvenc /tmp/tmp2.mp4"
                    os.system(command)
                    
                    if len(face) == 1:
                        #joins tmp2 with facecam into tmo_video
                        tmp_video = f"/tmp/final-{uuid.uuid1()}.mp4"
                        command = f"ffmpeg -c:v h264_cuvid -i /tmp/tmp2.mp4 -c:v h264_cuvid -i {file_name} -filter_complex \"overlay=x=(W/2)-(w/2):y=(H/2)+(h*1/4)\" -c:v h264_nvenc {tmp_video}"
                        os.system(command)
                    else:
                        tmp_video = "/tmp/tmp2.mp4"

                    #joins tmp2 with facecam into tmo_video old circle
                    """
                    tmp_video = f"/tmp/final-{uuid.uuid1()}.mp4"
                    command = f"ffmpeg -c:v h264_cuvid -i /tmp/tmp2.mp4 -c:v h264_cuvid -i {file_name} -filter_complex \"[1]trim=end_frame=1,  " \
                              f"geq='st(3,pow(X-(W/2),2)+pow(Y-(H/2),2));if(lte(ld(3),pow(min(W/2,H/2),2)),255," \
                              f"0)':10:10,setpts=N/FRAME_RATE/TB[mask];  [1][mask]alphamerge[cutout];  [0][" \
                              f"cutout]overlay=x=W/2-w/2:y=20[v];  [0][1]amix=2[a]\" -map \"[v]\" -map \"[a]\" -c:v h264_nvenc " \
                              f"{tmp_video} "
                    os.system(command) #y=50[v]
                    """


                    font = f"{ROOT_DIR}/resources/Metropolis-Black.otf"
                    game_tag = re.findall(r'videos/(.*)-.*', video)[0]

                    command = f"convert -background '#9D38FE' -size x200 -fill white -font {font} -gravity center " \
                              f"-pointsize 40 label:{game_tag.upper()} -extent 110%x /tmp/tag.png "
                    os.system(command)

                    command = f"convert -gravity east {ROOT_DIR}/resources/twitch.png -background '#9D38FE' -resize " \
                              f"100x100 -extent 180x200 -gravity east /tmp/logo-with-background.png "
                    os.system(command)

                    command = f"convert +append /tmp/logo-with-background.png /tmp/tag.png /tmp/tag-with-logo.png"
                    os.system(command)

                    command = f"convert /tmp/tag-with-logo.png -resize 300x300 /tmp/tag-rounded-resized.png"
                    os.system(command)

                    final_file_name = f"{ROOT_DIR}/{FACES_PATH}/final-{uuid.uuid1()}.mp4"
                    command = f"ffmpeg -c:v h264_cuvid -i {tmp_video} -i /tmp/tag-rounded-resized.png -filter_complex \"[0:v][" \
                              f"1:v] overlay=W/2-w/2:H/1.2+20'\" -pix_fmt yuv420p -c:a copy -c:v h264_nvenc {final_file_name}"
                    os.system(command)

                    ####ffmpeg -i input -t 5 -f lavfi -i anullsrc -filter_complex "color=duration=5:color=blue[bg];[bg][0]scale2ref[bg2][main];[bg2]setsar=1,drawtext=text='Ending':fontsize=20:x=(w-text_w)/2:y=(h-text_h)/2[text];[main][0:a][text][1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" output.mp4

                    # Clean tmp repository & face cropped video
                    try:
                        os.remove(os.path.join("/tmp", "tmp_back.mp4"))
                        os.remove(os.path.join("/tmp", "tmp_back1.mp4"))
                        os.remove(os.path.join("/tmp", "tmp_square.mp4"))
                        os.remove(os.path.join("/tmp", "tmp2.mp4"))
                        os.remove(os.path.join("/tmp", "tag.png"))
                        os.remove(os.path.join("/tmp", "logo-with-background.png"))
                        os.remove(os.path.join("/tmp", "tag-with-logo.png"))
                        os.remove(os.path.join("/tmp", "tag-rounded-resized.png"))
                        os.remove(tmp_video)
                        os.remove(file_name)
                    
                    cap.release()
                    break
            else:
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    num_process = 1

    # Download videos
    ##download.main(f"{ROOT_DIR}/resources/clips.txt", f"{ROOT_DIR}/videos/", '720')

    # Check faces directory
    check_directory(f"{ROOT_DIR}/{RESULTS_PATH}")
    check_directory(f"{ROOT_DIR}/{FACES_PATH}")

    list_of_videos = get_videos(DATASET_PATH)
    chunks = np.array_split(np.array(list_of_videos), num_process)
    process_pool = multiprocessing.Pool(processes=num_process, initializer=init_worker)

    init_worker()
    video_face_cropper(list_of_videos)

    print("End of Process !")
