from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'tip test',
    'author': 'Shawn Laursen',
    'description': '''Test tip continue.
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(protocol)
    tip_test(protocol)
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
    global tips300, tips300_2, p300m
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300_2])

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

def tip_test(protocol):
    for i in range(0,7):
        pickup_tips(8, p300m, protocol)
        p300m.drop_tip()
    for i in range(0,8):
        pickup_tips(1, p300m, protocol)
        p300m.drop_tip()
    for i in range(0,8):
        pickup_tips(1, p300m, protocol)
        p300m.drop_tip()
    pickup_tips(2, p300m, protocol)
    p300m.drop_tip()
    pickup_tips(3, p300m, protocol)
    p300m.drop_tip()
    pickup_tips(4, p300m, protocol)
    p300m.drop_tip()
    pickup_tips(5, p300m, protocol)
    p300m.drop_tip()
    pickup_tips(6, p300m, protocol)
    p300m.drop_tip()
    