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
    return shows[show_to_get]['title']

def check_available_episodes(show_title):
    return requests.get(
        'https://pbskids.org/pbsk/video/api/getVideos',
        params={
            'startindex': 1,
            'endindex': 45,
            'program': show_title,
            'status': 'available',
            'hls': 'true',
            'destination': 'producer',
            'type': 'Episode',
        }
    ).json()['items']

def ask_which_episode(available_episodes):
    print('Available Episodes:\n===================')
    index = 0
    for item in available_episodes:
        item['videos'] = item['videos']['hls']
        print(f'[{index}]: {item["title"]} - {item["description"]}\n')
        index += 1

    return int(input(f'Which episode do you want? [0-{index-1}]: '))

def ask_which_resolution():
    resolution_mapping = ['hls-2500k', 'hls-1080p']  # 720, 1080
    print('Available Resolutions:\n=====================:\n[0]: 720p\n[1]: 1080p')
    resolution_index = int(input('Which Resolution? [0-1]: '))
    return resolution_mapping[resolution_index]


def get_video_url(available_episodes, index_to_get, resolution):
    for key, values in available_episodes[index_to_get]['videos'].items():
        if key.startswith(resolution):
            return values['url']

def get_path_and_filename(video_url):
    r = requests.get(video_url, allow_redirects=False)
    location = r.headers['Location']
    manifest = requests.get(location).content.decode('utf-8')
    match_1080 = re.findall(
        '#EXT-X-STREAM.*RESOLUTION=(?P<resolution>1920x1080|1440x1080),.*\n(?P<filename>.*)\n',
        manifest
    )
    match_720 = re.findall(
        '#EXT-X-STREAM.*RESOLUTION=(?P<resolution>1280x720|960x720),.*\n(?P<filename>.*)\n',
        manifest
    )
    match = match_1080 or match_720
    filename = match[0][1]
    path = dirname(location)
    return path, filename

def get_output_filename(filename, show_title, episode_title, resolution):
    print(f'playlist: {filename}')
    patterns = (
        r'\w+[a-zA-Z](?P<season>\d{1,2})(?P<episode>\d{2})[-_]ep',
        r'\w+[_-]ep(?P<season>\d{1,2})(?P<episode>\d{2})[-_]',
        r'\w+[a-zA-Z](?P<season>\d{1,2})(?P<episode>\d{2})\w+[-_]ep',
        r'\w+[a-zA-Z](?P<season>\d{1,2})(?P<episode>\d{2})[-_].*m1080',
        r'\w+[a-zA-Z](?P<season>\d{1,2})(?P<episode>\d{2}).*h264[-_]\d+x\d+',
        r'\w+[a-zA-Z](?P<season>\d{1,2})(?P<episode>\d{2})[-_].*\d+x\d+',
    )

    for pattern in patterns:
        match = re.match(pattern, filename)
        if match:
            break

    # Prompt for season and episode to make sure it fits?
    season, episode = match.groups()
    season = season.zfill(2)
    output = f'{show_title} - S{season}E{episode} - {episode_title} - {resolution}.ts'
    output = output.replace('/', ' ')

    return output

def get_video_playlist_files(path, filename):
    playlist = requests.get(f'{path}/{filename}').content.decode('utf-8')
    return list(re.finditer('(?P<filename>.*\.ts)', playlist))

def create_output_file(playlist_files, output):
    print(f'Writing to: {output}')
    files = 1
    with open(output, 'wb') as f:
        for pfile in playlist_files:
            filename = pfile.groupdict()['filename']
            percentage = (files/len(playlist_files))*100
            print(
                f'[{percentage:.0f}%] {files}/{len(playlist_files)}: {filename}',
                end="\r",
                flush=True
            )
            bit = requests.get(f'{path}/{filename}')
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
    episode_title = available_episodes[index_to_get]['title']
    system('clear')
    resolution = ask_which_resolution()
    video_url = get_video_url(available_episodes, index_to_get, resolution)
    path, filename = get_path_and_filename(video_url)
    resolution_mapping = {'hls-2500k': '720p', 'hls-1080p': '1080p'}
    output = get_output_filename(
        filename, show_title, episode_title, resolution_mapping[resolution]
    )
    playlist_files = get_video_playlist_files(path, filename)
    create_output_file(playlist_files, output)
