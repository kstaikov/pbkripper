#!/usr/bin/env python3
import sys
import requests
import re
from os.path import dirname
from os import system
import os

download_subtitles = False # Set this to True if you want to download closed caption files as well
subtitle_type = "SRT" # Choose between Caption-SAMI, DFXP, SRT, and WebVTT

def get_shows():
    return requests.get(
        'https://pbskids.org/pbsk/video/api/getShows/'
    ).json()['items']

def ask_which_show(shows):
    show_index = 0
    for show in shows:
        print(f'[{show_index}]: {show["title"]} - {show["description"]}\n')
        show_index += 1

    show_to_get = int(input(f'Select a show: [0-{show_index-1}]: '))
    return shows[show_to_get]['cove_slug']

def check_available_episodes(show_title):
	url = 'https://cms-tc.pbskids.org/pbskidsvideoplaylists/' + show_title + '.json'
	return requests.get(url).json()['collections']['episodes']['content']

def ask_which_episode(available_episodes):
    print('Available Episodes for {}:\n==================='.format(
        available_episodes[0]['program']['title']))
    index = 0
    for item in available_episodes:
        print(f'[{index}]: {item["title"]} - {item["description"]}\n')
        index += 1

    return input(f'Which episode do you want? [0-{index-1}], A=All: ')

def get_video_info(video, subtitles=False):
    info = {}
    info['mp4'] = video['mp4']
    info['show_title'] = video['program']['title']
    info['episode_number'] = video['nola_episode']
    info['episode_title'] = video['title']
    if(info['episode_number'].isdigit()):
        if len(info['episode_number']) == 3:
            info['episode_number'] = "S{}E{}".format(
                int(info['episode_number'][0]), int(info['episode_number'][1:]))
        elif len(info['episode_number']) == 4:
            info['episode_number'] = "S{}E{}".format(
                int(info['episode_number'][0:1]), int(info['episode_number'][2:]))
    info['file_name'] = '{} - {} - {}.mp4'.format(
        info['show_title'], info['episode_number'], info['episode_title']).replace('/', ' & ')
    
    if( subtitles is not False):
        for item in video['closedCaptions']:
            if ( item['format'].lower() == subtitle_type.lower() ):
                info['subtitle_url'] = item['URI']
                #print(item['URI'])

        #print( video['closedCaptions'] )
    return info

def create_output_file(video_info):
    print(f"Writing to: {video_info['file_name']}")
    with open(video_info['file_name'], 'wb') as f:
        bit = requests.get(video_info['mp4'])
        f.write(bit.content)
        print('\nComplete!')
    
    if( 'subtitle_url' in video_info ):
        print("I will download subtitle file now.")
        file_extension = video_info['subtitle_url'].split(".")[-1:]
        file_extension = ''.join(file_extension)
        mp4_filename = os.path.basename(video_info['file_name'])
        subtitle_filename = str(os.path.splitext(mp4_filename)[0]) + "."+ file_extension
        print(f"Writing to: {subtitle_filename}")
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
    if(index_to_get.upper() == "A"):
        for item in available_episodes: # Download all episodes of selected show.
            video_info = get_video_info(item, download_subtitles)
            create_output_file(video_info)
    else:
        index_to_get = int(index_to_get)
    video_info = get_video_info(available_episodes[index_to_get], download_subtitles)
    create_output_file(video_info)