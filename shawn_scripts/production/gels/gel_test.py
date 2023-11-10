from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Gel load',
    'author': 'Shawn Laursen',
    'description': '''
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(protocol)
    foo(protocol)
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

def setup(protocol):
    #equiptment
    global tips300, tips300_2, p300m, trough, tempdeck, temp_pcr, tubes24
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300_2])
    trough = protocol.load_labware('nest_12_reservoir_15ml', 4)
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    tubes24 = protocol.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap', 11) 

    global sb
    sb = tubes24.rows()[0][0]

    #single tips
    global which_tips300, tip300
    which_tips300 = []
    tip300 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips300.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))
   
def pickup_tips(number, pipette, protocol):
    global tip300

    if pipette == p300m:
        if (tip300 % number) != 0:
            while (tip300 % 8) != 0:
                tip300 += 1
        tip300 += number-1
        if tip300 < 96:
            p300m.pick_up_tip(tips300[which_tips300[tip300]])
        else:
            p300m.pick_up_tip(tips300_2[which_tips300[tip300-96]])
        tip300 += 1

def foo(protocol):
    pickup_tips(1, p300m, protocol)
    p300m.aspirate(100, sb)
    p300m.dispense(100, trough.wells()[0])
    p300m.drop_tip()