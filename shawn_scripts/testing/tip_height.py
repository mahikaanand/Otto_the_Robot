from opentrons import protocol_api
import time
import sys
import math
#import pyttsx3
import random
import subprocess


metadata = {
    'protocolName': 'tip height',
    'author': 'Shawn Laursen',
    'description': '''Put mixes (50ul of protein+dna) and 250ul of (dna) next to
                      each other in 96 well plate
                      Titrates protein in 384well. ''',
    'apiLevel': '2.11'
    }

def run(protocol):

    well_96start = 0 #index from 0
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
    global tips300, plate96, plate96_2, p300m, tempdeck
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    plate96_2 = protocol.load_labware('costar_96_wellplate_200ul', 5)
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
    p300m.pick_up_tip()
    p300m.transfer(40, plate96.rows()[0][0],
                   plate96_2.rows()[0][0], new_tip='never')
    p300m.transfer(40, plate96.rows()[0][1].bottom(0),
                   plate96_2.rows()[0][1], new_tip='never')
    p300m.transfer(40, plate96.rows()[0][2].bottom(-1),
                   plate96_2.rows()[0][2], new_tip='never')
    p300m.drop_tip()
