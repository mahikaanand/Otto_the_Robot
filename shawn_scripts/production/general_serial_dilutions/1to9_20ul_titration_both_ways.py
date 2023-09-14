from opentrons import protocol_api
import time
import math


metadata = {
    'protocolName': 'Titration - 1 to 9, both ways',
    'author': 'Shawn Laursen',
    'description': '''Row1:
                      30ul 2x protein
                      100ul buff
                      100ul 2x DNA
                      Row2:
                      50ul 1x DNA+protein
                      200ul 1x DNA
                      
                      2 strip tubes in temp block.''',
    'apiLevel': '2.13'
    }

def run(protocol):
    well_96start = 0 #index from 0

    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    titrate_add_after(protocol)
    titrate_together(protocol)
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
    global trash, tips20, tips300, p20m, p300m, plate96, tempdeck, temp_pcr
    trash = protocol.fixed_trash['A1']
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul')

    global start_96well
    start_96well = well_96start

    #single tips
    global which_tips20, tip20
    which_tips20 = []
    tip20 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips20.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

    #single tips
    global which_tips300, tip300
    which_tips300 = []
    tip300 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips300.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

def titrate_add_after(protocol):
    global tip20, tip300
    enzy_col = start_96well
    buff_col = enzy_col+1
    samp_col = buff_col+1

    #add buff
    p300m.pick_up_tip(tips300[which_tips300[tip300]])
    tip300 += 1
    p300m.distribute(10, plate96.rows()[0][buff_col],
                     temp_pcr.rows()[0][1:7],
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()

    #titrate enzymes
    p20m.pick_up_tip(tips20[which_tips20[tip20]])
    tip20 += 1
    p20m.transfer(12, plate96.rows()[0][enzy_col],
                   temp_pcr.rows()[0][0], new_tip='never')
    for i in range(0,5):
        p20m.transfer(2, temp_pcr.rows()[0][i],
                   temp_pcr.rows()[0][i+1],
                   mix_after=(3, 5), new_tip='never')
    p20m.aspirate(2, temp_pcr.rows()[0][5])
    p20m.drop_tip()

    #add nucleic acid
    for i in range(0,7):
        p20m.pick_up_tip(tips20[which_tips20[tip20]])
        tip20 += 1
        p20m.aspirate(10, plate96.rows()[0][samp_col])
        p20m.dispense(10, temp_pcr.rows()[0][i])
        p20m.mix(3,10)
        p20m.drop_tip()

def titrate_together(protocol):
    global tip20, tip300
    enzy_col = start_96well
    buff_col = enzy_col+1
    samp_col = buff_col+1
    
    #add buff
    p300m.pick_up_tip(tips300[which_tips300[tip300]])
    tip300 += 1
    p300m.aspirate(175, plate96.rows()[1][buff_col])
    for i in range(1,7):
        p300m.dispense(20, temp_pcr.rows()[1][i])
    p300m.drop_tip()

    #titrate
    p300m.pick_up_tip(tips300[which_tips300[tip300]])
    tip300 += 1
    p300m.aspirate(22, plate96.rows()[1][enzy_col])
    p300m.dispense(22, temp_pcr.rows()[1][0])    
    p300m.drop_tip()
    p20m.pick_up_tip(tips20[which_tips20[tip20]])
    tip20 += 1
    for i in range(0,5):
        p20m.aspirate(2, temp_pcr.rows()[1][i])
        p20m.dispense(2, temp_pcr.rows()[1][i+1])
        p20m.mix(3,10)
    p20m.aspirate(2, temp_pcr.rows()[1][5])
    p20m.drop_tip()