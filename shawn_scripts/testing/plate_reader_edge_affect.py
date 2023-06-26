from opentrons import protocol_api
import time
import sys
import math
#import pyttsx3
import random
import subprocess


metadata = {
    'protocolName': 'Test plate',
    'author': 'Shawn Laursen',
    'description': '''Puts 20ul in all wells. Uses diiferent overage for even wells.''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0
    welcome(protocol)
    strobe(12, 8, True, protocol)
    setup(1, well_96start, protocol)
    for buff in buffs:
        protein_titration(buff, protocol)
    strobe(12, 8, False, protocol)

def strobe(blinks, hz, leave_on, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)

def setup(num_buffs, well_96start, protocol):
    #equiptment
    global tips300, plate96, plate384, p300m, tempdeck
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])

    #buffs
    global buffs, buffa, buffb, buffc, buffd
    buffa = "a"
    buffb = "b"
    buffc = "c"
    buffd = "d"
    buffs = [buffa, buffb, buffc, buffd]
    del buffs[num_buffs:]

    global start_96well
    start_96well = well_96start

def protein_titration(buff, protocol):
    buff_col = 4
    extra_buff_col = buff_col+1
    start_384well = 0
    which_rows = 0

    p300m.pick_up_tip()
    p300m.distribute(20, plate96.rows()[0][buff_col],
                     plate384.rows()[which_rows][start_384well:start_384well+12],
                     disposal_volume=10, new_tip='never')
    p300m.distribute(20, plate96.rows()[0][extra_buff_col],
                     plate384.rows()[which_rows][start_384well+12:start_384well+24],
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()

    which_rows = 1

    p300m.pick_up_tip()
    p300m.distribute(20, plate96.rows()[0][extra_buff_col+1],
                     plate384.rows()[which_rows][start_384well:start_384well+12],
                     disposal_volume=10, new_tip='never')
    p300m.distribute(20, plate96.rows()[0][extra_buff_col+2],
                     plate384.rows()[which_rows][start_384well+12:start_384well+24],
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()

def welcome(protocol):
    music('/data/songs/puccini.mp3', protocol)

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

if __name__=='__main__':
    main()
