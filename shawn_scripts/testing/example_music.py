from opentrons import protocol_api
import time
import sys
import math
#import pyttsx3
import random
import subprocess


metadata = {
    'protocolName': 'Example music script',
    'author': 'Shawn Laursen',
    'description': '''This script is an example of how to integrate music.
                      To update mp3s, you'll need to log on to the robot
                      through ssh and put them in the /data/songs folder.
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    welcome(protocol)
    #put functions here
    goodbye(protocol)

def welcome(protocol):
    if not protocol.is_simulating():
        mytime = time.localtime()
        if mytime.tm_hour in [6,7,8,9,10,11,12]:
            tod = 'welcome_morning.mp3'
            song = '2001.mp3'
        elif mytime.tm_hour in [13,14,15,16,17,18]:
            operas = [['Puccini', 'puccini.mp3'],
                      ['Verdi', 'verdi.mp3'],
                      ['Mozart','mozart.mp3'],
                      ['Haydn', 'haydn.mp3'],
                      ['Beethoven', 'beethoven.mp3']]
            num = random.randint(0, len(operas)-1)
            opera = operas[num]
            tod = 'welcome_{}.mp3'.format(opera[0])
            song = opera[1]
        elif mytime.tm_hour in [19,20,21,22,23]:
            tod = 'welcome_midday.mp3'
            song = 'get_it_started.mp3'
        else:
            tod = 'welcome_late.mp3'
            song = 'rockabye.mp3'

        general = 'welcome_general.mp3'
        music('/data/songs/'+tod, protocol)
        music('/data/songs/'+general, protocol)
        music('/data/songs/'+song, protocol)
    else:
        None

def goodbye(protocol):
    if not protocol.is_simulating():
        mytime = time.localtime()
        if mytime.tm_hour in [6,7,8,9,10,11,12]:
            tod = 'goodbye_morning.mp3'
        elif mytime.tm_hour in [13,14,15,16,17,18]:
            tod = 'goodbye_midmorning.mp3'
        elif mytime.tm_hour in [19,20,21,22,23]:
            tod = 'goodbye_midday.mp3'
        else:
            tod = 'goodbye_late.mp3'

        general = 'goodbye_general.mp3'
        music('/data/songs/'+tod, protocol)
        music('/data/songs/'+general, protocol)
    else:
        None

def run_quiet_process(command):
    subprocess.Popen('{} &'.format(command), shell=True)

def music(song, protocol):
    print('Speaker')
    print('Next\t--> CTRL-C')
    try:
        if not protocol.is_simulating():
            run_quiet_process('mpg123 {}'.format(song))
        else:
            print('Not playing mp3, simulating')
    except KeyboardInterrupt:
        pass
        print()