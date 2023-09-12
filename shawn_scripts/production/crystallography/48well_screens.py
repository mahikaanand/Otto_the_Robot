from opentrons import protocol_api
import time


metadata = {
    'protocolName': 'test_48well',
    'author': 'Shawn Laursen',
    'description': '''Test of 48well.''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(4, protocol)
    for plate in plates:
        add_screen(plate, protocol)
        add_drop(plate, protocol)
        add_protein(plate, protocol)
    strobe(12, 8, False, protocol)


def setup(num_buffs, protocol):
    #equiptment
    global tips20, tips20_2, tips300, plate48, plate48_2, screen_block, p20m, p300m, tempdeck, temp_pcr
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips20_2 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    plate48 = protocol.load_labware('hampton_48_wellplate_combine', 1)
    plate48_2 = protocol.load_labware('hampton_48_wellplate_combine', 3)
    screen_block = protocol.load_labware('thermoscientificnunc_96_wellplate_2000ul', 2)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20, tips20_2])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    
    global plates
    plates = [plate48, plate48_2]

def strobe(blinks, hz, leave_on, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)

def add_screen(plate, protocol):
    if plate == plate48:
        buffx = 0
    elif plate == plate48_2:
        buffx = 6

    p300m.transfer(200, 
                   screen_block.rows()[0][buffx:buffx+6],
                   plate.rows()[0][1:13:2], 
                   new_tip='always')

def add_drop(plate, protocol):
    p20m.transfer(2, 
                   plate.rows()[0][1:13:2],
                   plate.rows()[0][0:12:2], 
                   new_tip='always')

def add_protein(plate, protocol):
    p20m.transfer(2, 
                   temp_pcr.rows()[0][0],
                   plate.rows()[0][0:12:2], 
                   new_tip='always',
                   mix_after=(3,2))
