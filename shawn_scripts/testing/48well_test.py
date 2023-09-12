from opentrons import protocol_api
import time
import sys


metadata = {
    'protocolName': 'test_48well',
    'author': 'Shawn Laursen',
    'description': '''Test of 48well.''',
    'apiLevel': '2.11'
    }

def run(protocol):
    #setup
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    plate48 = protocol.load_labware('hampton_48_wellplate_200ul', 6)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    strobe(12, 8, True, protocol)
    p300m.pick_up_tip()
    p300m.transfer(20, 
                   plate48.rows()[0][0:5],
                   plate48.rows()[0][1:6], 
                   new_tip='never')
    p300m.drop_tip()
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
