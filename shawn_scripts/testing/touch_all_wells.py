from opentrons import protocol_api
import time
import sys
import math
#import pyttsx3
import random
import subprocess


metadata = {
    'protocolName': 'Touch all',
    'author': 'Shawn Laursen',
    'description': '''Makes buffers from stocks in 24 well thermal module.
                      Plates mixes into 96well.
                      Titrates salt mixes in 96well.
                      Titrates protein in 384well. ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(4, protocol)
    for buff in buffs:
        make_mixes(buff, protocol)
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
    mixes = [hpd, lpd, hd, ld]

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
    p300m.pick_up_tip()
    p300m.distribute(20, plate96.rows()[0][0],
                     plate96.rows()[0][0:12],
                     disposal_volume=0, new_tip='never')
    p300m.distribute(20, plate384.rows()[0][0],
                     plate384.rows()[0][0:24],
                     disposal_volume=0, new_tip='never')
    p300m.drop_tip()