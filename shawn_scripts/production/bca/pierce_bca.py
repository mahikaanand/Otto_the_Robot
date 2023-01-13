from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'BCA (Pierce)',
    'author': 'Shawn Laursen',
    'description': '''This protocol will perform the Pierce BCA protocol.
                      Place 500ul of 2mg/ml BSA in A1 of Temp deck 24well.
                      Place 60ul protein in top row in the third column and on.
                      Place 2 (+ num samples) x 8 strip tubes in 96well aluminum block.
                      Place dilution buffer in column 1 of trough.
                      Place 1200ul x # samples + 5000ul of mixed BCA reagent
                      in column 2 of trough. Robot will make BSA standard dilution
                      in first 2 columns specified, put 60ul your protein(s) in
                      first tube of third (and on strips). Robot will make 1:1
                      dilution series of your protein. After standard and
                      experimental dilutions are made, robot will add 200ul of
                      working reagent to each well (30ul of protein is used in
                      all wells). Don't forget alter the program with number of
                      samples and where to start on the 96well plate (indexed
                      from 0).
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    num_samples = 1
    well_96start = 0 #index from 0

    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    #make_standards(protocol)
    for sample in range(0, num_samples):
        titrate(sample, protocol)
    add_wr(num_samples, protocol)
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

def setup(well_96start, protocol):
    #equiptment
    global tips300, tips300_2, trough, plate384, p300m, plate96, pcr_strips
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300_2])
    p300m.flow_rate.aspirate = 40
    p300m.flow_rate.dispense = 40
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 5)
    pcr_strips = protocol.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul', 6)
    tempdeck = protocol.load_module('temperature module gen2', 10)
    global temp_buffs
    temp_buffs = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')

    global buffer, working, bsa
    buffer = trough.wells()[0]
    working = trough.wells()[1]
    bsa = temp_buffs.wells_by_name()['A1'].bottom(-2)

    global start_96well
    start_96well = well_96start

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

def make_standards(protocol):
    global tip, tip_col

    dilutants = [25,65,35,65,65,65,80]
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for strip in [0,1]:
        count = 1
        for dilute in dilutants:
            p300m.aspirate(dilute, buffer)
            p300m.dispense(dilute, pcr_strips.rows()[count][strip])
            count += 1
    p300m.drop_tip()

    for strip in [0,1]:
        count = 0
        standards = [[60, bsa],
                     [75, bsa],
                     [65, bsa],
                     [35, pcr_strips.rows()[1][strip]],
                     [65, pcr_strips.rows()[2][strip]],
                     [65, pcr_strips.rows()[4][strip]],
                     [65, pcr_strips.rows()[5][strip]]]

        for standard in standards:
            p300m.pick_up_tip(tips300[which_tips[tip]])
            tip += 1
            p300m.aspirate(standard[0], standard[1])
            p300m.dispense(standard[0], pcr_strips.rows()[count][strip])
            p300m.mix(3,40)
            p300m.drop_tip()
            count += 1

        p300m.pick_up_tip(tips300_2[which_tip_col[tip_col]])
        tip_col += 1
        p300m.transfer(30, pcr_strips.rows()[0][strip],
                       plate96.rows()[0][start_96well+strip],
                       new_tip='never')
        p300m.drop_tip()

def titrate(sample, protocol):
    global tip, tip_col

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.aspirate(210, buffer)
    for row in range(1,8):
        p300m.dispense(30, pcr_strips.rows()[row][sample+2])
    p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for row in range(0,7):
        p300m.aspirate(30, pcr_strips.rows()[row][sample+2])
        p300m.dispense(30, pcr_strips.rows()[row+1][sample+2])
        p300m.mix(3,30)
    p300m.aspirate(30, pcr_strips.rows()[7][sample+2])
    p300m.drop_tip()

    p300m.pick_up_tip(tips300_2[which_tip_col[tip_col]])
    tip_col += 1
    p300m.transfer(30, pcr_strips.rows()[0][sample+2],
                   plate96.rows()[0][start_96well+sample+2], new_tip='never')
    p300m.drop_tip()

def add_wr(num_samples, protocol):
    global tip_col

    p300m.pick_up_tip(tips300_2[which_tip_col[tip_col]])
    for col in range(start_96well, start_96well+num_samples+2):
        p300m.distribute(200, working, plate96.rows()[0][col].top(),
                         disposal_volume=0, new_tip='never')
    p300m.drop_tip()
