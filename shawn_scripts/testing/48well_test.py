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
    p300m.pick_up_tip()
    p300m.transfer(20, 
                   plate48.rows()[0][0:4],
                   plate48.rows()[0][1:5], 
                   new_tip='never')
    p300m.drop_tip()
 
