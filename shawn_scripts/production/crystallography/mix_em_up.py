from opentrons import protocol_api
import time
import math


metadata = {
    'protocolName': 'Crystallography - mix em up',
    'author': 'Shawn Laursen',
    'description': '''Mixes the screens from the 96well plate
                      uses 16 tips, goes from low to high.''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(protocol)
    mix_em(protocol)
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
    global tips300, plate96, p300m
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    plate96 = protocol.load_labware('thermoscientificnunc_96_wellplate_2000ul', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])

def mix_em(protocol):
    p300m.pick_up_tip()
    for col in reversed(range(0,6)):
        p300m.mix(repetitions=5, volume=300, location=plate96.rows()[0][col])
    p300m.drop_tip()
    
    p300m.pick_up_tip()
    for col in reversed(range(6,12)):
        p300m.mix(repetitions=5, volume=300, location=plate96.rows()[0][col])
    p300m.drop_tip()
