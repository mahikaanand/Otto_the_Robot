import time
import subprocess
from opentrons import protocol_api

metadata = {
    'protocolName': 'Get it started',
    'author': 'Parrish Payne <protocols@opentrons.com>',
    'description': 'Tests out the speaker system on the OT-2',
    'apiLevel': '2.11'
}

AUDIO_FILE_PATH = '/data/songs/get_it_started.mp3'

def run_quiet_process(command):
    subprocess.Popen('{} &'.format(command), shell=True)

def test_speaker(protocol):
    print('Speaker')
    print('Next\t--> CTRL-C')
    try:
        if not protocol.is_simulating():
            run_quiet_process('mpg123 {}'.format(AUDIO_FILE_PATH))
        else:
            print('Not playing mp3, simulating')
    except KeyboardInterrupt:
        pass
        print()

def strobe(blinks, hz, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(True)

def run(protocol):
    test_speaker(protocol)
    strobe(50, 3, protocol)
