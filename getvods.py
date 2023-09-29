from chat_downloader import ChatDownloader
from time import sleep
import os
import csv
from random import randint
from datetime import datetime, timedelta
import sys
import requests


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

os.system("rm -r ./videos")
os.system("mkdir ./videos")
os.system("cd ./videos")

# Set up authentication
client_id = 'sqr118ehr13u78lui4fh2iv27jcorh'
client_secret = '<your_client_secret>'
access_token = '29k4e3pdl56pmtanbg7fxjjdr02895'

# Make the API request
username = sys.argv[1]
getid_url = f'https://api.twitch.tv/helix/users?login={username}'
headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {access_token}'
}
response = requests.get(getid_url, headers=headers)

# Process the response
if response.status_code == 200:
    data = response.json()
    user_id = data['data'][0]['id']
    print(f"The Twitch ID for {username} is {user_id}")
else:
    print("Error occurred while making the API request")


getvods_url = f'https://api.twitch.tv/helix/videos?user_id={user_id}'
headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {access_token}'
}
params = {
    'first': 10,
    'sort': 'time',
    'type': 'archive'
}
response = requests.get(getvods_url, headers=headers, params=params)

# Process the response
if response.status_code == 200:
    data = response.json()
    vods = data['data']
    
    # Sort the VODs by duration
    sorted_vods = sorted(vods, key=lambda vod: (len(vod['duration']), vod['duration']) ,reverse=True)

    # Get the VOD IDs and durations
    vod_ids = [vod['id'] for vod in sorted_vods]
    vod_durations = [vod['duration'] for vod in sorted_vods]

    vod_links10 = ["https://www.twitch.tv/videos/"+vod['id'] for vod in sorted_vods]
    print(vod_links10)

    vod_links = vod_links10[0:4]
    print (vod_links)
    # Print the sorted VOD IDs and durations
    #for vod_id, vod_duration in zip(vod_ids, vod_durations):
    #    print(f"VOD ID: {vod_id} - Duration: {vod_duration}")
else:
    print("Error occurred while making the API request")

###############


file_1= 'cliptime.csv'

with open(file_1, 'w+') as filehandle:
    filehandle.write("")

for vod in vod_links:
    peak_times = find_peak_times(vod)
    for time in peak_times:
        time_start = time + timedelta(seconds=30)
        time_end = time - timedelta(seconds=30)
        try:
            with open(file_1, 'a+') as filehandle: ##a+ to keep old w+ to start new
                filehandle.write('%s,%s,%s,%s\n' % (vod, time, time_start, time_end))
        except:
            print('errorfile')
        #print(vod, time)

#os.system("cd videos")

with open('cliptime.csv') as csvfile:
    csvstring = csvfile.read() + '\n'
    lines = csvstring.splitlines()
    reader = csv.reader(lines)
    csvdata = list(reader)


for clip_no in range(0,59):
    link = csvdata[clip_no][0]
    #Mid_time = csvdata[clip_no][1]
    start_time = csvdata[clip_no][3]
    end_time = csvdata[clip_no][2]

    s_t = start_time[11:19]
    e_t = end_time[11:19]
    #twitch-dl download <videos> -q 720p -s hh:mm:ss -e hh:mm:ss

    command1 = f"twitch-dl download {link} -f mp4 -q source -s {s_t} -e {e_t}"+" -o ./videos/{channel}-"+f"{clip_no}_"+".{format}"
    command = command1
    print(command)

    os.system(command)
 
 
