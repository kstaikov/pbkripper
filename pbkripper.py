#!/usr/bin/env python3
import sys
import requests
import re
from os.path import dirname
from os import system

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

    return int(input(f'Which episode do you want? [0-{index-1}]: '))

def get_video_info(video):
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
    return info

def create_output_file(video_info):
    print(f"Writing to: {video_info['file_name']}")
    files = 1
    with open(video_info['file_name'], 'wb') as f:
        bit = requests.get(video_info['mp4'])
        f.write(bit.content)
        files += 1
        print('\nComplete!')

if __name__ == '__main__':
    shows = get_shows()
    show_title = ask_which_show(shows)
    available_episodes = check_available_episodes(show_title)
    if not available_episodes:
        sys.exit(f'No episodes available for series: "{show_title}". Try another show next time.')
    system('clear')
    index_to_get = ask_which_episode(available_episodes)
    video_info = get_video_info(available_episodes[index_to_get])
    create_output_file(video_info)