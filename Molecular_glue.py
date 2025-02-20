from opentrons import protocol_api
import time
import sys
import math
import random
import subprocess


metadata = {
    'protocolName': 'Molecular Glue',
    'author': 'Johannes Rudolph',
    'description': '''Adds 20 uL of buffer to all wells (need 8.5 mL)
                      Then adds 20 uL of 2x PARP1 - HPF1 mix to all wells (need 8.5 mL)
                      Adds 1 uL of compound (in duplicate) from two different compound plates
                      Uses 2 rows of p20 and of p300 tips each''',
    'apiLevel': '2.18'
    }

def run(protocol):
    
    # run protocol
    strobe(12, 8, True, protocol)
    setup(protocol)
    fill_plate_buffer(protocol)
    fill_plate_PARP_HPF1_mix(protocol)    
    add_cmpds(protocol)
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
    # equipment
    global plate96_1, plate96_2, plate384, tips20, tips300, trough, p20m, p300m
    plate96_1 = protocol.load_labware('costar_96_wellplate_200ul',1)
    plate96_2 = protocol.load_labware('costar_96_wellplate_200ul',2)
    plate384 = protocol.load_labware('corning3575_384well_alt', 3)
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    trough = protocol.load_labware('nest_12_reservoir_15ml', 6)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=[tips20])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tips300])

    # reagents
    global buffer
    buffer = trough.wells()[0]
    global PARP_HPF1_mix
    PARP_HPF1_mix = trough.wells()[1]

    # tips
    #global tip20_dict, tip300_dict
    #tip20_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}
    #tip300_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}

#def pickup_tips(number, pipette, protocol):
    # if pipette == p20m:
    #     for col in tip20_dict:
    #         if len(tip20_dict[col]) >= number:
    #             p20m.pick_up_tip(tips20[str(tip20_dict[col][number-1] + str(col))])
    #             tip20_dict[col] = tip20_dict[col][number:]
    #             break

    #if pipette == p300m:
    #   for col in tip300_dict:
    #        if len(tip300_dict[col]) >= number:
    #            p300m.pick_up_tip(tips300[str(tip300_dict[col][number-1] + str(col))])
    #            tip300_dict[col] = tip300_dict[col][number:]
    #            break

def fill_plate_buffer(protocol):
    p300m.pick_up_tip()
    p300m.distribute(20, buffer,
        plate384.rows()[0:2][0:24],
        disposal_volume=7,
        new_tip='never')
    p300m.drop_tip()

def fill_plate_PARP_HPF1_mix(protocol):
    p300m.pick_up_tip()
    p300m.distribute(20, PARP_HPF1_mix,
        plate384.rows()[0:2][0:24],
        disposal_volume=7,
        new_tip='never')
    p300m.drop_tip()

def add_cmpds(protocol):
    # put 1 uL of compounds into all columns of 384 well plate, both on left and right side of plate
    p20m.pick_up_tip()
    for i in range(0,12):
        p20m.aspirate(1, plate96_1.rows()[0][i])
        p20m.dispense(1, plate384.rows()[0][i])
        p20m.blow_out()
        p20m.aspirate(1, plate96_1.rows()[0][i])
        p20m.dispense(1, plate384.rows()[0][i+12])
        p20m.blow_out()
    p20m.drop_tip()
    p20m.pick_up_tip()
    for i in range(0,12):
        p20m.aspirate(1, plate96_2.rows()[0][i])
        p20m.dispense(1, plate384.rows()[1][i])
        p20m.blow_out()
        p20m.aspirate(1, plate96_2.rows()[0][i])
        p20m.dispense(1, plate384.rows()[1][i+12])
        p20m.blow_out()
    p20m.drop_tip()
    
