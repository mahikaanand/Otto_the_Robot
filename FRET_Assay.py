from opentrons import protocol_api
import time
import sys
import math
import random
import subprocess

metadata = {
    'protocolName': 'VariableFRET',
    'author': 'Johannes Rudolph',
    'description': '''You put in 96 well plate: 
                        - 2x titrant protein (volume = 10x # of samples + 50 uL) 
                            into col 1, 3, and 5, OR 7, 9, and 11 (user choice) of row A
                      You put into 12-well trough:
                        - 10ml buffer in col 1
                        - 1 mL of control label in col 2
                        - 1 mL of sample in col 3 to xx (depending on how many samples you have)

                      Robot:
                        - Add buffer to 96-well plate
                        - Titrate titrant protein in zig-zag pattern in 96-well plate (in 2 columns); do this 3x
                        - Add buffer to 384-well plate (columns 1-6)
                        - Add titrant protein to 384-well plate (columns 4 -24 (as needed); in every third row)
                        - Add control to 384-well plate (columns 1 - 3)
                        - Add samples to 384-well plate (columns 7-24, as needed) ''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="col_to_start",
        display_name="column to start",
        description="Column to start serial dilution of acceptor.",
        default=1,
        minimum=1,
        maximum=7,
        unit="column"
    )

    parameters.add_int(
        variable_name="number_of_samples",
        display_name="number of samples",
        description="Number of samples",
        default=1,
        minimum=1,
        maximum=6,
        unit="column"
    )

def run(protocol):
    # set variables
    col_to_start = protocol.params.col_to_start
    number_of_samples = protocol.params.number_of_samples
    dilution_volume = number_of_samples * 10 + 10 + 40

    # where to pick up tips
    well_96start = 0 #index from 0
    
    # run protocol
    strobe(12, 8, True, protocol)
    setup(protocol)
    #dilution(col_to_start, protocol, dilution_volume)
    distribution (col_to_start, number_of_samples, protocol)
    sample_addition (number_of_samples, protocol)
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
    #equipment
    global tips20, tips300, p20m, p300m, trough, buffer, control, sample, plate96, plate384
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    trough = protocol.load_labware('nest_12_reservoir_15ml', 4)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 5)
    plate384 = protocol.load_labware('corning3575_384well', 6)    

    #reagents
    buffer = trough.wells()[0]
    control = trough.wells()[1]

    # tips
    global tip300_dict
    tip300_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}

def pickup_tips(number, pipette, protocol):
    if pipette == p300m:
        for col in tip300_dict:
            if len(tip300_dict[col]) >= number:
                p300m.pick_up_tip(tips300[str(tip300_dict[col][number-1] + str(col))])
                tip300_dict[col] = tip300_dict[col][number:]
                break

#Add buffer and then dilute FRET acceptor in 96-well plate; 3x to get replicates
def dilution(col_to_start, protocol, dilution_volume):
    # add (number of samples *10 + 40) µL of buff to all dilution wells
    pickup_tips(8, p300m, protocol)
    p300m.distribute(dilution_volume, buffer, plate96.rows()[0][col_to_start-1:col_to_start+5],new_tip='never')
    p300m.drop_tip()

    #do the serial dilution   
    for i in [0,2,4]:
        pickup_tips(1, p300m, protocol)
        p300m.aspirate(dilution_volume, plate96.rows()[0][col_to_start+i-1])
        p300m.mix(3,dilution_volume)
        p300m.dispense(dilution_volume, plate96.rows()[0][col_to_start+i])
        p300m.mix(3,dilution_volume)  

        for row in range(1,8):
            p300m.aspirate(dilution_volume, plate96.rows()[row-1][col_to_start+i])
            p300m.dispense(dilution_volume, plate96.rows()[row][col_to_start+i-1])
            p300m.mix(3,dilution_volume)
            
            p300m.aspirate(dilution_volume, plate96.rows()[row][col_to_start+i-1])
            p300m.dispense(dilution_volume, plate96.rows()[row][col_to_start+i])
            p300m.mix(3,dilution_volume)
        p300m.aspirate(dilution_volume, plate96.rows()[row][col_to_start+i])
        p300m.drop_tip()

#Add buffer to 384 well plate and then add titrant protein for control and for samples (in divisi triplicates)
def distribution(col_to_start, number_of_samples, protocol):
    pickup_tips(8, p300m, protocol)
    for i in range(0,2):
            p300m.distribute(10, buffer,
                    plate384.rows()[i][0:6],
                    disposal_volume=0,
                    new_tip='never')

    for i in [0,2,4]:
        for j in range(1,number_of_samples+2):
            p300m.distribute(10, plate96.rows()[0][col_to_start+i-1],
                    plate384.rows()[0][3*j+int(i/2)],
                    disposal_volume=0,
                    new_tip='never')

    for i in [0,2,4]:
        for j in range(1,number_of_samples+2):
            p300m.distribute(10, plate96.rows()[0][col_to_start+i],     
                    plate384.rows()[1][3*j+int(i/2)],
                    disposal_volume=0,
                    new_tip='never')
    p300m.drop_tip()

#Add control and samples to 384 well plate (in adjacent triplicates)
def sample_addition(number_of_samples, protocol):
        pickup_tips(8, p300m, protocol)
        for i in range(0,2):
            p300m.distribute(10, control,
                plate384.rows()[i][0:3],
                disposal_volume=0,
                new_tip='never')
        p300m.drop_tip()

        for i in range(0,number_of_samples):
                pickup_tips(8, p300m, protocol)
                for j in range(0,2):
                        p300m.distribute(10, trough.wells()[i+2],
                            plate384.rows()[j][3*i+6:3*i+9],
                            disposal_volume=0,
                            new_tip='never')
                p300m.drop_tip()
    

