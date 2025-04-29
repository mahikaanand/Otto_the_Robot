"""Schmear Assay Opentrons Protocol"""
import math
import time
from opentrons import protocol_api

metadata = {
    'protocolName': 'Schmear Assay Sample Prep for PARP ± HPF1',
    'author': 'Helen Brackney',
    'description': '''Takes buffer mixed with p18mer and PARP ± HPF1
                      and plates it into a 384 well plate.
                      Add compound from a 96 well plate to the
                      appropriate wells in the 384 well plates.
                      Adds NAD+ mix, waits for the specified time
                      and then quenches the reaction with the
                      quenching mix.
                      
                      Buffers needed in the trough:
                      Column A: 6.5 mL of PARP mixture
                      Column B: 6.5 mL of PARP + HPF1 mixture
                      Column C: 5.5 mL of NAD+ Mixture
                      Column D: 4.5 mL of Quenching Mixture''',
    'apiLevel': '2.11'
    }

def run(protocol):
    """This function contains everything need to start
    and run the schmear assay protocol."""
    # Start-up Seqeunce
    strobe(12, 8, True, protocol)
    setup(protocol)

    # Adding Protein Buffer
    buffer_plate_fill(30, protocol)

    # Adding Compound
    compound_plate_add(1, plate96, plate96_2, protocol)

    start_time = time.time()
    # Adding NAD+ Mix
    add_nad_mix(10, protocol)

    # Running Time
    runtime = 5*60 # minutes to seconds
    current_time = time.time()
    wait_time = abs(current_time - (start_time + runtime))
    time.sleep(wait_time)

    # Adding Quenching Mix
    add_quenching_mix(7.5, protocol)

    # Ending Sequence
    strobe(12, 8, False, protocol)

def strobe(blinks, hz, leave_on, protocol):
    """This function controls the beginning
    and ending strobe seqeunce."""
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)

def setup(protocol):
    """This function creates the labware and
    equiment as global variables so they can be
    called in later."""
    # Equipment
    global trough, tips300, plate96, plate96_2, plate384, p300m
    trough = protocol.load_labware('nest_12_reservoir_15ml', 3)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 1)
    plate96_2 = protocol.load_labware('costar_96_wellplate_200ul', 2)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])

    global tips20_1, tips20_2, tips20_3, tips20_4, p20m
    tips20_1 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    tips20_2 = protocol.load_labware('opentrons_96_tiprack_20ul', 7)
    tips20_3 = protocol.load_labware('opentrons_96_tiprack_20ul', 8)
    tips20_4 = protocol.load_labware('opentrons_96_tiprack_20ul',9)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20_1, tips20_2,
                                                tips20_3, tips20_4])

    # Mixes
    global PARPmix, PARP_HPF1mix , NADmix, Quenchmix
    PARPmix = trough.wells()[0] # Buffer with PARP
    PARP_HPF1mix = trough.wells()[1] # Buffer with PARP + HPF1
    NADmix = trough.wells()[2] # NAD+ Mix
    Quenchmix = trough.wells()[3] # Quenching Mix

    #single tips
    global which_tips300, tip300
    which_tips300 = []
    tip300 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips300.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

    global which_tips20, tip20
    which_tips20 = []
    tip20 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips20.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

    #tip columns
    global which_tip_col, tip_col
    which_tip_col = []
    tip_col = 0
    for i in range(1,13):
        which_tip_col.append('A'+str(i))

def pickup_tips(number, pipette, tip_rack, protocol):
    """This function defines the pickup routine for the
    pipetting arms."""
    global tip300, tip20

    if pipette == p300m:
        if (tip300 % number) != 0:
            while (tip300 % 8) != 0:
                tip300 += 1
        tip300 += number-1
        p300m.pick_up_tip(tip_rack[which_tips300[tip300]])
        tip300 += 1

    # if pipette == p20m:
    #     if (tip20 % number) != 0:
    #         while (tip20 % 8) != 0:
    #             tip20 += 1
    #     tip20 += number-1
    #     p20m.pick_up_tip(tip_rack[which_tips20[tip20]])
    #     tip20 += 1

def buffer_plate_fill(amount, protocol):
    """Disperses buffer over entire plate.

    Args:
        amount (int): amount of solution to be dispered per well
        protocol (Opentrons Protocol): needed for each
    """
    pickup_tips(8, p300m, tips300, protocol)
    counter = 0
    # Adding Parp Mix
    for row in range(0,2):
        for col in range (0,12):
            if counter < amount:
                p300m.aspirate(240, PARPmix.bottom(1)) # PARP Mix
                counter += 240
            p300m.dispense(amount, plate384.rows()[row][col])
            counter -= amount
    #p300m.drop_tip()
    
    # Adding HPF1 Mix
    #pickup_tips(8, p300m, tips300, protocol)
    counter = 0
    for row in range(0,2):
        for col in range(12,24):
            if counter < amount:
                p300m.aspirate(240, PARP_HPF1mix.bottom(1)) # PARP + HPF1 Mix
                counter += 240
            p300m.dispense(amount, plate384.rows()[row][col])
            counter -= amount
    p300m.drop_tip()

def compound_plate_add(amount, com_plate, com_plate2, protocol):
    """Disperses buffer over entire plate.

    Args:
        amount (int): amount of solution to be dispered per well
        protocol (Opentrons Protocol): needed for each
    """
    for col in range(0,12):
        # PARP Odd Rows
        p20m.pick_up_tip() # pickup_tips(1, p20m, tips20_1, protocol)
        p20m.aspirate(amount, com_plate.rows()[0][col])
        p20m.dispense(amount, plate384.rows()[0][col])
        for _ in range(3):
            p20m.aspirate(15, plate384.rows()[0][col])
            p20m.dispense(15, plate384.rows()[0][col])
        p20m.drop_tip()

        # PARP Mix Even Rows
        p20m.pick_up_tip() #pickup_tips(1, p20m, tips20_1, protocol)
        p20m.aspirate(amount, com_plate2.rows()[0][col])
        p20m.dispense(amount, plate384.rows()[1][col])
        for _ in range(3):
            p20m.aspirate(15, plate384.rows()[1][col])
            p20m.dispense(15, plate384.rows()[1][col])
        p20m.drop_tip()

    for col in range(0,12):
        # Adding Compound to Parp HPF1 Mix Columns Odd Rows
        p20m.pick_up_tip() #pickup_tips(1, p20m, tips20_2, protocol)
        p20m.aspirate(amount, com_plate.rows()[0][col])
        p20m.dispense(amount, plate384.rows()[0][col + 12])
        for _ in range(3):
            p20m.aspirate(15, plate384.rows()[0][col + 12])
            p20m.dispense(15, plate384.rows()[0][col + 12])
        p20m.drop_tip()

        # PARP + HPF1 Mix Even Rows
        p20m.pick_up_tip() #pickup_tips(1, p20m, tips20_3, protocol)
        p20m.aspirate(amount, com_plate2.rows()[0][col])
        p20m.dispense(amount, plate384.rows()[1][col + 12])
        for _ in range(3):
            p20m.aspirate(15, plate384.rows()[1][col + 12])
            p20m.dispense(15, plate384.rows()[1][col + 12])
        p20m.drop_tip()

def add_nad_mix(amount, protocol):
    """This function add NAD+ mix to every well in the
    first 15 rows of the plate and the first six and third
    six in the bottom row of the plate."""
    # TODO: Pick up seven and do the top 15 rows and then pick up one and do six 
    pickup_tips(7, p300m, tips300, protocol)
    counter = 0
    for row in range(0,2):
        for col in range (0,12):
            if counter < amount:
                p300m.aspirate(245, NADmix.bottom(1)) # NAD Mix
                counter += 245
            p300m.dispense(amount, plate384.rows()[row][col])
            counter -= amount
    for row in range(0,2):
        for col in range (12,24):
            if counter < amount:
                p300m.aspirate(245, NADmix.bottom(1)) # NAD Mix
                counter += 245
            p300m.dispense(amount, plate384.rows()[row][col])
            counter -= amount
    p300m.drop_tip()

    pickup_tips(1, p300m, tips300, protocol)
    counter = 0
    for col in range(0,24):
        if counter < amount:
            p300m.aspirate(240, NADmix.bottom(1)) # NAD Mix
            counter += 240
        p300m.dispense(amount, plate384.rows()[14][col])
        counter -= amount
    p300m.drop_tip()

    pickup_tips(1, p300m, tips300, protocol)
    counter = 0
    for col in [0,1,2,3,4,5,12,13,14,15,16,17]:
        if counter < amount:
            p300m.aspirate(130, NADmix.bottom(0.5)) # NAD Mix
            counter += 130
        p300m.dispense(amount, plate384.rows()[15][col])
        counter -= amount
    p300m.drop_tip()

def add_quenching_mix(amount, protocol):
    """This function add quenching mix to every well in the plate."""
    pickup_tips(7, p300m, tips300, protocol)
    counter = 0
    for row in range(0,2):
        for col in range (0,12):
            if counter < amount:
                p300m.aspirate(173, Quenchmix.bottom(1), rate = 0.3) # Quenching Mix
                protocol.delay(seconds=5)
                counter += 173
            p300m.dispense(amount, plate384.rows()[row][col])
            counter -= amount
    for row in range(0,2):
        for col in range (12,24):
            if counter < amount:
                p300m.aspirate(173, Quenchmix.bottom(1), rate = 0.3) # Quenching Mix
                protocol.delay(seconds=5)
                counter += 173
            p300m.dispense(amount, plate384.rows()[row][col])
            counter -= amount
    p300m.drop_tip()

    pickup_tips(1, p300m, tips300, protocol)
    counter = 0
    for col in range(0,24):
        if counter < amount:
            p300m.aspirate(173, Quenchmix.bottom(1), rate = 0.3) # Quenching  Mix
            protocol.delay(seconds=5)
            counter += 173
        p300m.dispense(amount, plate384.rows()[14][col])
        counter -= amount
    p300m.drop_tip()

    pickup_tips(1, p300m, tips300, protocol)
    counter = 0
    for col in [0,1,2,3,4,5,12,13,14,15,16,17]:
        if counter < amount:
            p300m.aspirate(90, Quenchmix.bottom(0.5), rate = 0.3 ) # Quenching Mix
            protocol.delay(seconds=5)
            counter += 90
        p300m.dispense(amount, plate384.rows()[15][col])
        counter -= amount

    for col in [6,7,8,9,10,11,18,19,20,21,22,23]:
        if counter < amount:
            p300m.aspirate(90, Quenchmix.bottom(0.5), rate = 0.3) # Quenching Mix
            protocol.delay(seconds=5)
            counter += 90
        p300m.dispense(amount, plate384.rows()[15][col])
        counter -= amount
    p300m.drop_tip()
