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

def setup(protocol):
    #equiptment
    global tips20_single, tips20_multi, p20m
    tips20_single = protocol.load_labware('opentrons_96_tiprack_20ul', '6')
    tips20_multi = protocol.load_labware('opentrons_96_tiprack_20ul', '3')
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20_single, tips20_multi])

    global gDNA_plate, out_plate, index_plate, tempdeck
    gDNA_plate = protocol.load_labware(
        'biorad_96_wellplate_200ul_pcr', '1', 'gDNA plate')
    out_plate = protocol.load_labware(
        'biorad_96_wellplate_200ul_pcr', '5', 'output plate')
    index_plate = protocol.load_labware(
        'biorad_96_wellplate_200ul_pcr', '4', 'index plate')
    tempdeck = protocol.load_module('temperature module gen2', 10)

    global num_cols
    num_cols = math.ceil(num_samples/8)

    #reagents
    global temp_buffs, atm, td, nt, npm, indexes
    temp_buffs = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')
    atm = temp_buffs.wells()[0]  # Amplicon Tagment Mix
    td = temp_buffs.wells()[1]  # Tagment DNA Buffer
    nt = temp_buffs.wells()[2]  # Neutralize Tagment Buffer
    npm = temp_buffs.wells()[3]  # Nextera PCR Master Mix
    indexes = index_plate.rows()[0][:num_cols]

    #single tips
    global which_tips, tip
    which_tips = []
    tip = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

    #tip columns
    global which_tip_col, tip_col
    which_tip_col = []
    tip_col = 0
    for i in range(1,13):
        which_tip_col.append('A'+str(i))

def tagmentation(protocol):
    global tip, tip_col

    # Add Tagment DNA Buffer to each well
    for out in range(0, num_samples):
        p20m.pick_up_tip(tips20_single[which_tips[tip]])
        tip += 1
        p20m.aspirate(10, td)
        p20m.dispense(10, out_plate.wells()[out])
        p20m.blow_out()
        p20m.drop_tip()

    # Add normalized gDNA to each well
    for col in range(0, num_cols):
        p20m.pick_up_tip(tips20_multi[which_tip_col[tip_col]])
        tip_col += 1
        p20m.aspirate(5, gDNA_plate.rows()[0][col])
        p20m.dispense(5, out_plate.rows()[0][col])
        p20m.blow_out()
        p20m.drop_tip()

    # Add ATM to each well
    for out in range(0, num_samples):
        p20m.pick_up_tip(tips20_single[which_tips[tip]])
        tip += 1
        p20m.aspirate(5, atm)
        p20m.dispense(5, out_plate.wells()[out])
        p20m.mix(5,10)
        p20m.blow_out()
        p20m.drop_tip()

    protocol.pause("Centrifuge at 280 × g at 20°C for 1 minute. Place \
    on the preprogrammed thermal cycler and run the tagmentation program. When \
    the sample reaches 10°C, immediately proceed to the next step because the \
    transposome is still active. Place the plate back to slot 2.")

    # Add Neutralize Tagment Buffer to each well
    for out in range(0, num_samples):
        p20m.pick_up_tip(tips20_single[which_tips[tip]])
        tip += 1
        p20m.aspirate(5, nt)
        p20m.dispense(5, out_plate.wells()[out])
        p20m.mix(5,10)
        p20m.blow_out()
        p20m.drop_tip()

    protocol.pause("Centrifuge at 280 × g at 20°C for 1 minute. Place \
    the plate back on slot 2.")

    # Incubate at RT for 5 minutes
    protocol.delay(minutes=5)

def amplify(protocol):
    global tip, tip_col

    # Add each index
    for col in range(0, num_cols):
        p20m.pick_up_tip(tips20_multi[which_tip_col[tip_col]])
        tip_col += 1
        p20m.aspirate(10, index_plate.rows()[0][col])
        p20m.dispense(10, out_plate.rows()[0][col])
        p20m.mix(5,10)
        p20m.blow_out()
        p20m.drop_tip()

    # Add Nextera PCR Master Mix to each well
    for out in range(0, num_samples):
        p20m.pick_up_tip(tips20_single[which_tips[tip]])
        tip += 1
        p20m.aspirate(15, npm)
        p20m.dispense(15, out_plate.wells()[out])
        p20m.mix(2,10)
        p20m.blow_out()
        p20m.drop_tip()
