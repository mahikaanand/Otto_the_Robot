from opentrons import protocol_api
import time
import sys
import math
#import pyttsx3
import random
import subprocess


metadata = {
    'protocolName': 'High salt buffer screen',
    'author': 'Shawn Laursen',
    'description': '''Makes buffers from stocks in 24 well thermal module.
                      Does not make high salt buffs -> make and put in 24well.
                      Plates mixes into 96well.
                      Titrates salt mixes in 96well.
                      Titrates protein in 384well. ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    welcome(protocol)
    strobe(12, 8, True, protocol)
    setup(4, protocol)
    for buff in buffs:
        make_mixes(buff, protocol)
        plate_96well(buff, protocol)
        plate_controls(buff, protocol)
        salt_titration(buff, protocol)
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
    global trough, tips300, tips300_2, plate96, plate384, p300m, tempdeck
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300_2])
    tempdeck = protocol.load_module('temperature module gen2', 10)
    global temp_buffs
    temp_buffs = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')

    #buffs
    global buffs, buffa, buffb, buffc, buffd
    buffa = trough.wells()[0]
    buffb = trough.wells()[1]
    buffc = trough.wells()[2]
    buffd = trough.wells()[3]
    buffs = [buffa, buffb, buffc, buffd]
    del buffs[num_buffs:]

    #components
    global components
    high_salt = trough.wells()[4]
    low_salt = trough.wells()[5]
    edta = trough.wells()[6]
    water = trough.wells()[7]
    protein = temp_buffs.wells_by_name()['A1']
    dna = temp_buffs.wells_by_name()['A2']
    dna_extra = temp_buffs.wells_by_name()['D2']
    components = [high_salt, low_salt, edta, water, protein, dna, dna_extra]

    #mixes
    global mixes, hpd, lpd, hd, ld
    hpd = {'comps': [edta, high_salt, dna, protein], 'vol': 150, 'loc': None}
    lpd = {'comps': [edta, low_salt, dna, protein], 'vol': 350, 'loc': None}
    hd = {'comps': [edta, high_salt, water, dna], 'vol': 550, 'loc': None}
    ld = {'comps': [edta, low_salt, water, dna_extra], 'vol': 1500, 'loc': None}
    mixes = [lpd, ld]

    #single tips
    global which_tips, tip
    which_tips = []
    tip = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

    #tip columns
    global which_tip_col, tip_col
    which_tip_col = []
    tip_col = 0
    for i in range(1,13):
        which_tip_col.append('A'+str(i))

def make_mixes(buff, protocol):
    global tip
    bc = buffs.index(buff)+2
    hpd['loc'] = temp_buffs.rows()[0][bc].top()
    lpd['loc'] = temp_buffs.rows()[1][bc].top()
    hd['loc'] = temp_buffs.rows()[2][bc].top()
    ld['loc'] = temp_buffs.rows()[3][bc].top()

    for component in components:
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for mix in mixes:
            if component in mix['comps']:
                p300m.aspirate(mix['vol']/5, component)
                p300m.dispense(mix['vol']/5, mix['loc'])
                p300m.touch_tip()
                p300m.blow_out(mix['loc'])
        p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for mix in mixes:
        p300m.aspirate(mix['vol']/5, buff)
        p300m.dispense(mix['vol']/5, mix['loc'])
        p300m.touch_tip()
        p300m.blow_out(mix['loc'])
    p300m.drop_tip()

def plate_96well(buff, protocol):
    global tip
    bc = buffs.index(buff)+2
    hpd['loc'] = temp_buffs.rows()[0][bc]
    lpd['loc'] = temp_buffs.rows()[1][bc]
    hd['loc'] = temp_buffs.rows()[2][bc]
    ld['loc'] = temp_buffs.rows()[3][bc]
    prot_col = buffs.index(buff)*2
    buff_col = prot_col+1
    extra_col = buffs.index(buff)+8

    #plate high salt protein
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3, 50, hpd['loc'])
    p300m.aspirate(100, hpd['loc'].bottom(-2))
    p300m.dispense(100, plate96.rows()[1][prot_col].bottom(1.75))
    p300m.blow_out(plate96.rows()[1][prot_col])
    p300m.drop_tip()

    #plate low salt protein
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3, 100, lpd['loc'])
    p300m.aspirate(300, lpd['loc'].bottom(-2))
    for row in range(2,8):
        p300m.dispense(50, plate96.rows()[row][prot_col].bottom(1.75))
    p300m.blow_out(plate96.rows()[7][prot_col])
    p300m.drop_tip()

    #move buff wells
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3, 250, hd['loc'])
    p300m.aspirate(270, hd['loc'].bottom(-2))
    p300m.dispense(270, plate96.rows()[1][extra_col].bottom(1.75))
    p300m.blow_out(plate96.rows()[1][extra_col])
    p300m.aspirate(230, hd['loc'].bottom(-2))
    p300m.dispense(230, plate96.rows()[1][buff_col].bottom(1.75))
    p300m.blow_out(plate96.rows()[1][buff_col])
    p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3, 250, ld['loc'])
    for row in range(2,8):
        p300m.aspirate(250, ld['loc'].bottom(-2))
        p300m.dispense(135, plate96.rows()[row][extra_col].bottom(1.75))
        p300m.dispense(115, plate96.rows()[row][buff_col].bottom(1.75))
        p300m.blow_out(plate96.rows()[row][extra_col])
    p300m.drop_tip()

def plate_controls(buff, protocol):
    global tip
    prot_col = buffs.index(buff)*2
    buff_col = prot_col+1
    extra_col = buffs.index(buff)+8
    if buffs.index(buff) < 2:
        pr = 1
        br = 1
    else:
        pr = 2
        br = 2

    #move protein
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.aspirate(50, temp_buffs.rows()[pr][0].bottom(-2))
    p300m.dispense(50, plate96.rows()[0][prot_col].bottom(1.75))
    p300m.blow_out(plate96.rows()[0][prot_col])
    p300m.drop_tip()

    #move buff
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.aspirate(250, temp_buffs.rows()[br][1].bottom(-2))
    p300m.dispense(115, plate96.rows()[0][buff_col].bottom(1.75))
    p300m.dispense(135, plate96.rows()[0][extra_col].bottom(1.75))
    p300m.blow_out()
    p300m.drop_tip()

def salt_titration(buff, protocol):
    global tip
    prot_col = buffs.index(buff)*2
    buff_col = prot_col+1
    extra_col = buffs.index(buff)+8

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for row in range(1,6):
        p300m.aspirate(50, plate96.rows()[row][prot_col].bottom(1.75))
        p300m.dispense(50, plate96.rows()[row+1][prot_col].bottom(1.75))
        p300m.mix(3,50)
    p300m.aspirate(50, plate96.rows()[6][prot_col].bottom(1.75))
    p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for row in range(1,6):
        p300m.aspirate(115, plate96.rows()[row][buff_col].bottom(1.75))
        p300m.dispense(115, plate96.rows()[row+1][buff_col].bottom(1.75))
        p300m.mix(3,115)
    p300m.aspirate(115, plate96.rows()[6][buff_col].bottom(1.75))
    p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for row in range(1,6):
        p300m.aspirate(135, plate96.rows()[row][extra_col].bottom(1.75))
        p300m.dispense(135, plate96.rows()[row+1][extra_col].bottom(1.75))
        p300m.mix(3,135)
    p300m.aspirate(135, plate96.rows()[6][extra_col].bottom(1.75))
    p300m.drop_tip()

def protein_titration(buff, protocol):
    global tip_col
    prot_col = buffs.index(buff)*2
    buff_col = prot_col+1
    extra_col = buffs.index(buff)+8
    if (buffs.index(buff) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    if buffs.index(buff) < 2:
        start_384well = 0
    else:
        start_384well = 12

    p300m.pick_up_tip(tips300_2[which_tip_col[tip_col]])
    tip_col += 1
    p300m.transfer(125, plate96.rows()[0][extra_col].bottom(1.75),
                   plate96.rows()[0][buff_col],
                   new_tip='never')
    p300m.distribute(20, plate96.rows()[0][buff_col].bottom(1.75),
                     plate384.rows()[which_rows][start_384well+1:start_384well+12],
                     disposal_volume=0, new_tip='never')
    p300m.blow_out()
    p300m.transfer(40, plate96.rows()[0][prot_col].bottom(1.75),
                   plate384.rows()[which_rows][start_384well], new_tip='never')
    p300m.blow_out()
    p300m.transfer(20,
                   plate384.rows()[which_rows][start_384well:start_384well+10],
                   plate384.rows()[which_rows][start_384well+1:start_384well+11],
                   mix_after=(3, 20), new_tip='never')
    p300m.blow_out()
    p300m.aspirate(20, plate384.rows()[which_rows][start_384well+10])
    p300m.drop_tip()

def say_message(message):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    nationality = 'uk'
    if nationality == 'French':
        engine.setProperty('voice', voices[38].id)
    else:
        engine.setProperty('voice', voices[7].id)

    engine.say(message)
    engine.runAndWait()

def welcome(protocol):
    if not protocol.is_simulating():
        mytime = time.localtime()
        if mytime.tm_hour in [6,7,8,9,10,11,12]:
            tod = 'My stars, you\'re here early. Let\'s get you pumped up.'
            song = '2001.mp3'
        elif mytime.tm_hour in [13,14,15,16,17,18]:
            operas = [['Puccini', 'puccini.mp3'],
                      ['Verdi', 'verdi.mp3'],
                      ['Mozart','mozart.mp3'],
                      ['Haydn', 'haydn.mp3'],
                      ['Beethoven', 'beethoven.mp3']]
            num = random.randint(0, len(operas)-1)
            opera = operas[num]
            print(opera)
            tod = 'Good morning Johannes, how about some {}?'.format(opera[0])
            song = opera[1]
        elif mytime.tm_hour in [19,20,21,22,23]:
            tod = 'Let\'s do some pipetting!'
            song = 'get_it_started.mp3'
        else:
            tod = 'You\'re here late!'
            song = 'rockabye.mp3'

        general = 'Go take a break, I\'ve got this.'
        #say_message(tod)
        #say_message(general)
        music('/data/songs/'+song, protocol)
    else:
        None

def goodbye(protocol):
    if not protocol.is_simulating():
        mytime = time.localtime()
        if mytime.tm_hour in [6,7,8,9,10,11,12]:
            tod = 'Make this a great day!'
        elif mytime.tm_hour in [13,14,15,16,17,18]:
            tod = 'Have a great rest of your day!'
        elif mytime.tm_hour in [19,20,21,22,23]:
            tod = 'Almost done for the day!'
        else:
            tod = 'Now go to bed!'

        general = 'That\'s all for me! '
        say_message(general)
        say_message(tod)
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
