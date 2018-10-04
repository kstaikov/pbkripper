#!/usr/bin/env python3
import sys
import requests
import re
from os.path import dirname
from os import system
import os
import json
from tqdm import tqdm
import math

DOWNLOAD_ROOT = '.'
DOWNLOAD_SUBTITLES = True
SUBTITLE_TYPE = 'SRT'

def get_shows():
    return requests.get('https://pbskids.org/pbsk/video/api/getShows/').json()['items']

def ask_which_show(shows):
    show_index = 0
    for show in shows:
        print(f'[{show_index}]: {show["title"]} - {show["description"]}\n')
        show_index += 1

    show_to_get = int(input(f'Select a show: [0-{show_index-1}]: '))
    return shows[show_to_get]['cove_slug']

def check_available_episodes(show_title):
    url = f'https://cms-tc.pbskids.org/pbskidsvideoplaylists/{show_title}.json'
    return requests.get(url).json()['collections']['episodes']['content']

def ask_which_episode(available_episodes):
    print('Available Episodes for {}:\n==================='.format(
        available_episodes[0]['program']['title']))
    index = 0
    for item in available_episodes:
        print(f'[{index}]: {item["title"]} - {item["description"]}\n')
        index += 1

    return input(f'Which episode do you want? [0-{index-1}], A=All: ')

def get_video_info(video, subtitles="False"):
    info = {}
    info['mp4'] = video['mp4']
    info['id'] = video['id']
    info['slug'] = video['program']['slug']
    info['show_title'] = video['program']['title'].strip()
    info['episode_number'] = video['nola_episode'] # A lot of episodes seem to not include a real number, so most of the time this is just an abbreviation of the show title
    info['episode_title'] = video['title']
    if info['episode_number'].isdigit():
        if len(info['episode_number']) == 3: # If episode number is like 301, split so it becomes S3E01
            info['episode_number'] = "S{}E{}".format(
                int(info['episode_number'][0]), int(info['episode_number'][1:]))
        elif len(info['episode_number']) == 4: # If episode number is 1210, split so it becomes S12E10
            info['episode_number'] = "S{}E{}".format(
                int(info['episode_number'][0:1]), int(info['episode_number'][2:]))
    info['base_file_name'] = '{} - {} - {}'.format(
        info['show_title'], info['episode_number'], info['episode_title']).replace('/', ' and ')
    info['video_file'] = os.path.join(DOWNLOAD_ROOT, info['show_title'], info['base_file_name'])

    if not subtitles:
        for item in video['closedCaptions']:
            if ( item['format'].lower() == SUBTITLE_TYPE.lower() ):
                info['subtitle_url'] = item['URI']

    return info

def create_output_file(video_info):
    video_dir = os.path.dirname(video_info['video_file']+".mp4")
    os.makedirs(video_dir, exist_ok=True)
    mp4_file = video_info['video_file']+".mp4"
    if os.path.exists(mp4_file):
        print("path exists. not downloading.")
        d = {'slug': video_info['slug'], 'videofile': mp4_file}
    else:
        print(f"Writing to: {mp4_file}.")
        bit = requests.get(video_info['mp4'], stream=True)
        total_size = int(bit.headers.get('content-length', 0));
        block_size = 1048576
        wrote = 0
        with open(mp4_file, 'wb') as f, tqdm(bit.iter_content(block_size),total=math.ceil(total_size/block_size), unit='MB') as progress_bar:
            for data in progress_bar:
                wrote = wrote  + len(data)
                f.write(data)
            d = {'slug': video_info['slug'], 'videofile': mp4_file}
            if total_size != 0 and wrote != total_size:
                print("ERROR, something went wrong")

    if 'subtitle_url' in video_info:
        subtitle_extension = video_info['subtitle_url'].split(".")[-1:]
        subtitle_extension = ''.join(subtitle_extension)
        subtitle_filename = video_info['video_file']+"."+subtitle_extension
        if not os.path.exists(subtitle_filename):
            print(f"Writing to: {subtitle_filename}.")
            with open(subtitle_filename, 'wb') as s:
              bit = requests.get(video_info['subtitle_url'])
              s.write(bit.content)
              print('\nComplete!')

if __name__ == '__main__':
    shows = get_shows()
    show_title = ask_which_show(shows)
    available_episodes = check_available_episodes(show_title)
    if not available_episodes:
        sys.exit(f'No episodes available for series: "{show_title}". Try another show next time.')
    system('clear')
    index_to_get = ask_which_episode(available_episodes)
    if index_to_get.upper() == "A": # Download all episodes of selected show
        for item in available_episodes:
            video_info = get_video_info(item, DOWNLOAD_SUBTITLES)
            create_output_file(video_info)
    else: # Download only selected episode
        index_to_get = int(index_to_get)
        video_info = get_video_info(available_episodes[index_to_get], DOWNLOAD_SUBTITLES)
        create_output_file(video_info)
