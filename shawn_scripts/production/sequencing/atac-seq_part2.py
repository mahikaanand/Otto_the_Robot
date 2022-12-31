from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'ATAC-seq 0',
    'author': 'Shawn Laursen',
    'description': '''This protocol will perform the first steps in the Nextera
                      XT DNA library prep protocol: tagmentation and
                      amplification. (Based on Opentrons protocol)
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    global num_samples
    num_samples = 1

    strobe(8, 8, True, protocol)
    setup(protocol)
    tagmentation(protocol)
    amplify(protocol)
    strobe(8, 8, False, protocol)

def strobe(blinks, hz, leave_on, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)
