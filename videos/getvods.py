from chat_downloader import ChatDownloader
from time import sleep
import os
import csv
from random import randint
from datetime import datetime, timedelta


def find_peak_times(vod):

    chat = ChatDownloader().get_chat(vod,output="chat.txt")
    for message in chat:
        donothing = True
        #chat.print_formatted(message)

    message_counts = {}
    format = "%H:%M:%S"

    with open("chat.txt", 'r') as file:
        lines = file.readlines()
        #print (lines)
    for line in lines:
        
        timestamp_start = line.find("|") - 8
        timestamp_end = line.find("|") - 1
        timestamp = line[0:timestamp_end]
        
        if len(timestamp) == 4:
            timestamp = "00:0" + timestamp

        
        if len(timestamp) == 5:
            timestamp = "00:" + timestamp


        # Parse timestamp and round it to the nearest 30 seconds
        dt = datetime.strptime(timestamp, format)
        rounded_dt = dt - timedelta(seconds=dt.second % 30)

        # Count messages for each 30-second segment
        if rounded_dt in message_counts:
            message_counts[rounded_dt] += 1
        else:
            message_counts[rounded_dt] = 1

    # Find the 5 segments with the most messages
    peak_times = sorted(message_counts.keys(), key=lambda x: message_counts[x], reverse=True)[:10]

    return peak_times





vod_links = ('https://www.twitch.tv/videos/1896762513','https://www.twitch.tv/videos/1894994632','https://www.twitch.tv/videos/1894155462','https://www.twitch.tv/videos/1893713165','https://www.twitch.tv/videos/1891564537')

file_1= 'cliptime.csv'

with open(file_1, 'w+') as filehandle:
    filehandle.write("a")

for vod in vod_links:
    peak_times = find_peak_times(vod)
    for time in peak_times:
        time_start = time + timedelta(seconds=45)
        time_end = time - timedelta(seconds=45) 
        try:
            with open(file_1, 'a+') as filehandle: ##a+ to keep old w+ to start new
                filehandle.write('%s,%s,%s,%s\n' % (vod, time, time_start, time_end))
        except:
            print('errorfile')
        #print(vod, time)


with open('cliptime.csv') as csvfile:
    csvstring = csvfile.read() + '\n'
    lines = csvstring.splitlines()
    reader = csv.reader(lines)
    csvdata = list(reader)


for clip_no in range(0,59):
    link = csvdata[clip_no][0]
    #Mid_time = csvdata[clip_no][1]
    start_time = csvdata[clip_no][2]
    end_time = csvdata[clip_no][3]

    s_t = start_time[11:19]
    e_t = end_time[11:19]
    #twitch-dl download <videos> -q 720p -s hh:mm:ss -e hh:mm:ss
    command = f"twitch-dl download {link} -f mp4 -q source -s {s_t} -e {e_t}"+" -o {channel}-"+f"{s_t}"+".{format}"
    os.system(command)
