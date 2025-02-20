from opentrons import protocol_api
import time
import sys
import math
import random
import subprocess


metadata = {
    'protocolName': 'FP assay',
    'author': 'Johannes Rudolph, adapted from Shawn Laursen',
    'description': '''Does up to 8 different samples (in duplicate, titrated, 3:2's) with one labeled DNA.
                      Put as many 1 ml eppis in 24 well holder as you have samples with 100 uL of 1.5x highest protein concentration
                        (tubes ordered by columns)
                      Put labeled DNA (at 3x conc) into first well of trough:
                        (need 1 mL for each sample + 1 mL overage)
                      Uses 4 rows of tips if there are 8 samples''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="number_of_samples",
        display_name="number of samples",
        description="The number of samples you want to assay, in duplicate.",
        default=1,
        minimum=1,
        maximum=8,
        unit="column"
    )

def run(protocol):
    # set variables
    number_of_samples = protocol.params.number_of_samples
    
    # run protocol
    strobe(12, 8, True, protocol)
    setup(protocol)
    fill_plate_dna(protocol, number_of_samples)    
    titrate_protein(protocol,number_of_samples)
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
    global tips300, plate384, p300m, rt_24, trough
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tips300])
    rt_24 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 8)
    trough = protocol.load_labware('nest_12_reservoir_15ml', 2)

    # reagents
    global dna
    dna = trough.wells()[0]

    # tips
    global tip20_dict, tip300_dict
    tip20_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}
    tip300_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}

def pickup_tips(number, pipette, protocol):
    # if pipette == p20m:
    #     for col in tip20_dict:
    #         if len(tip20_dict[col]) >= number:
    #             p20m.pick_up_tip(tips20[str(tip20_dict[col][number-1] + str(col))])
    #             tip20_dict[col] = tip20_dict[col][number:]
    #             break

    if pipette == p300m:
        for col in tip300_dict:
            if len(tip300_dict[col]) >= number:
                p300m.pick_up_tip(tips300[str(tip300_dict[col][number-1] + str(col))])
                tip300_dict[col] = tip300_dict[col][number:]
                break

def fill_plate_dna(protocol, number_of_samples):
    pickup_tips(number_of_samples, p300m, protocol)
    p300m.distribute(20, dna,
        plate384.rows()[0:2][0:24],
        disposal_volume=0,
        new_tip='never')
    p300m.drop_tip()

def titrate_protein(protocol, number_of_samples):
    # put prot into col 1 of 384 well plate 
    for i in range(0,number_of_samples):
        pickup_tips(1, p300m, protocol)
        p300m.aspirate(90, rt_24.wells()[i])
        for j in range(0,2):
            p300m.dispense(40, plate384.rows()[2*i+j][0])
        p300m.drop_tip()
    
    # titrate protein
    for i in range(0,2):
        pickup_tips(number_of_samples, p300m, protocol)
        p300m.transfer(40,
                    plate384.rows()[i][0:21],
                    plate384.rows()[i][1:22],
                    mix_after=(3, 30), new_tip='never')
        p300m.aspirate(40, plate384.rows()[i][21])
        p300m.drop_tip()
