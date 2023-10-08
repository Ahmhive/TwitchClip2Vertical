#!/usr/bin/env python3

import os
import re
import sys
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
                    
        q = randint(10,9000)
        os.system(f"rm -r {ROOT_DIR}/tmp/{q}")
        os.system(f"mkdir {ROOT_DIR}/tmp/{q}/")

        random_frames = np.random.randint(1, 199, 10)
        frame_no = 0

        cap = cv2.VideoCapture(video)
        cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 0)

        while cap.isOpened():
            frame_no += 1

            # remove tmp if exist
            ##os.system(f"rm -rf /tmp/tmp*")

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
                        file_name = f"{ROOT_DIR}/tmp/{q}/{uuid.uuid1()}.mp4"
                        ffmpeg.crop(stream, x, y, x2 - x, y2 - y).output(stream.audio, file_name,
                                                                        s="%sx%s" % (600, 500)).run()

                    ###make tmp2
                    command = f"ffmpeg -c:v h264_cuvid -resize 1920x1080 -i {video} -c:a copy -c:v h264_nvenc -b:v 5M {ROOT_DIR}/tmp/{q}/tmp_square1.mp4" #makes square
                    os.system(command)

                    command = f"ffmpeg -c:v h264_cuvid -crop 0x0x420x420 -i {ROOT_DIR}/tmp/{q}/tmp_square1.mp4 -c:a copy -c:v h264_nvenc -b:v 5M {ROOT_DIR}/tmp/{q}/tmp_square.mp4" #makes square
                    os.system(command)

                    start_sec = randint(0,14000)
                    yt_start=(timedelta(seconds=start_sec))


                    command = f"ffmpeg -c:v h264_cuvid -crop 150x150x370x370 -resize 1080x840 -i {ROOT_DIR}/background.mp4 -ss {yt_start} -t 58 -c:a copy -c:v h264_nvenc -b:v 5M {ROOT_DIR}/tmp/{q}/tmp_back.mp4"# makkes background
                    os.system(command)

                    command = f"ffmpeg -c:v h264_cuvid -i {ROOT_DIR}/tmp/{q}/tmp_square.mp4 -c:v h264_cuvid -i {ROOT_DIR}/tmp/{q}/tmp_back.mp4 -vsync 2 -filter_complex vstack -map 0:a -c:v h264_nvenc {ROOT_DIR}/tmp/{q}/tmp2.mp4"
                    os.system(command)
                    
                    ###face =5555
                    if len(face)== 1:
                        #joins tmp2 with facecam into tmo_video
                        tmp_video = f"{ROOT_DIR}/tmp/{q}/tmp3.mp4"
                        command = f"ffmpeg -c:v h264_cuvid -i {ROOT_DIR}/tmp/{q}/tmp2.mp4 -c:v h264_cuvid -i {file_name} -filter_complex \"overlay=x=(W/2)-(w/2):y=(H/2)+(h*1/4)\" -c:v h264_nvenc {tmp_video}"
                        os.system(command)
                    else:
                        tmp_video = f"{ROOT_DIR}/tmp/{q}/tmp2.mp4"

                    font = f"{ROOT_DIR}/resources/Metropolis-Black.otf"
                    game_tag = re.findall(r'videos/(.*)-.*', video)[0]
                    vidnum = re.findall(r'videos/.*-(.*)_.*', video)[0]

                    command = f"convert -background white -size x200 -fill '#9D38FE' -font {font} -gravity center " \
                                f"-pointsize 40 label:{game_tag.upper()} -extent 110%x {ROOT_DIR}/tmp/{q}/tag.png "
                    os.system(command)

                    command = f"convert -gravity east {ROOT_DIR}/resources/twitch2.png -background white -resize " \
                                f"400x200 -extent 480x200 -gravity east {ROOT_DIR}/tmp/{q}/logo-with-background.png "
                    os.system(command)

                    command = f"convert +append {ROOT_DIR}/tmp/{q}/logo-with-background.png {ROOT_DIR}/tmp/{q}/tag.png {ROOT_DIR}/tmp/{q}/tag-with-logo.png"
                    os.system(command)

                    command = f"convert {ROOT_DIR}/tmp/{q}/tag-with-logo.png -resize 500x300 {ROOT_DIR}/tmp/{q}/tag-rounded-resized.png"
                    os.system(command)

                    final_file_name = f"{ROOT_DIR}/{FACES_PATH}/short{vidnum}.mp4"
                    command = f"ffmpeg -c:v h264_cuvid -i {tmp_video} -i {ROOT_DIR}/tmp/{q}/tag-rounded-resized.png -filter_complex \"[0:v][" \
                                f"1:v] overlay=W/2-w/2:H/1.2+20'\" -pix_fmt yuv420p -t 58 -c:a copy -c:v h264_nvenc {final_file_name}"
                    os.system(command)

                    try:
                        os.system(f"rm -r {ROOT_DIR}/tmp/{q}/")
                        os.remove(tmp_video)
                        os.remove(file_name)
                    except:
                        nothing11= True
                        
                    cap.release()
                    break
            else:
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    num_process = 4

    os.system(f"rm -r {ROOT_DIR}/videos")
    os.system(f"mkdir {ROOT_DIR}/videos")
    os.system(f"rm -r {ROOT_DIR}/results")


    twitchname = sys.argv[1]
    command = f"python3 getvods.py {twitchname}"
    os.system(command)

    # Download background
    command = f"yt-dlp  -o background.mp4 -f mp4  https://www.youtube.com/embed/RMeYn4E5WMY"
    os.system(command)


    # Check faces directory
    check_directory(f"{ROOT_DIR}/{RESULTS_PATH}")
    check_directory(f"{ROOT_DIR}/{FACES_PATH}")

    list_of_videos = get_videos(DATASET_PATH)
    chunks = np.array_split(np.array(list_of_videos), num_process)
    process_pool = multiprocessing.Pool(processes=num_process, initializer=init_worker)
    print("list_of_videos",list_of_videos)
    print("chunks", chunks)
    print("process_pool", process_pool)


    init_worker()
    video_face_cropper(list_of_videos)

    #send to vultr
    directory = f"{ROOT_DIR}/{FACES_PATH}"

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            print(f)
            command = f"echo n |  pscp -pw '2d(Ca8x-G7ouqdiZ' {f} root@45.76.136.237:/root/Desktop/{twitchname}/temp"
            os.system(command)
    
    print("End of Process !")
