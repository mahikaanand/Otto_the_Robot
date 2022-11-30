from opentrons import protocol_api
import time
import sys
import math
#import pyttsx3
import random
import subprocess


metadata = {
    'protocolName': 'Protein titration - 24 well',
    'author': 'Shawn Laursen',
    'description': '''Put mixes (50ul of protein+dna) and 2x250ul of (dna) next to
                      each other in 96 well plate
                      Titrates protein in 384well. ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    #welcome(protocol)
    strobe(12, 8, True, protocol)
    setup(2, protocol)
    for buff in buffs:
        protein_titration(buff, protocol)
    #goodbye(protocol)
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

def setup(num_buffs, protocol):
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

def protein_titration(buff, protocol):
    prot_col = buffs.index(buff)*3
    buff_col = prot_col+1
    extra_buff_col = buff_col+1
    start_384well = 0
    if (buffs.index(buff) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    p300m.pick_up_tip()
    p300m.distribute(20, plate96.rows()[0][buff_col].bottom(1.75),
                     plate384.rows()[which_rows][start_384well+1:start_384well+12],
                     disposal_volume=0, new_tip='never')
    p300m.blow_out()
    p300m.distribute(20, plate96.rows()[0][extra_buff_col].bottom(1.75),
                     plate384.rows()[which_rows][start_384well+12:start_384well+24],
                     disposal_volume=0, new_tip='never')
    p300m.blow_out()
    p300m.transfer(40, plate96.rows()[0][prot_col].bottom(1.75),
                   plate384.rows()[which_rows][start_384well], new_tip='never')
    p300m.blow_out()
    p300m.transfer(20,
                   plate384.rows()[which_rows][start_384well:start_384well+22],
                   plate384.rows()[which_rows][start_384well+1:start_384well+23],
                   mix_after=(3, 20), new_tip='never')
    p300m.blow_out()
    p300m.aspirate(20, plate384.rows()[which_rows][start_384well+22])
    p300m.drop_tip()

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
