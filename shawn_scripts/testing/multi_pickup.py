from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'testing',
    'author': 'Shawn Laursen',
    'description': '''Testing
                      ''',
    'apiLevel': '2.18'
    }


def run(protocol):
    strobe(12, 8, True, protocol)
    setup(protocol)
    test(protocol)    
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
    # equiptment
    global tips20,p20m
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=[tips20, tips20_2])

    #single tips
    global tip20_dict
    tip20_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}

def pickup_tips(number, pipette, protocol):
    for col in tip20_dict:
        if len(tip20_dict[col]) >= number:
            p20m.pick_up_tip(tips20[str(tip20_dict[col][number-1] + str(col))])
            tip20_dict[col] = tip20_dict[col][number:]
            break
        
def test(protocol):
    for j in range(0,3):
        pickup_tips(7, p20m, protocol)
        p20m.drop_tip()
