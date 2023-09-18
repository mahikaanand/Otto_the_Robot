from opentrons import protocol_api
import time
import math


metadata = {
    'protocolName': 'Titration - 1 to 9, togther',
    'author': 'Shawn Laursen',
    'description': '''col0 50ul 1x DNA+protein
                      col1 200ul 1x DNA
                      strip tubes in temp block.''',
    'apiLevel': '2.13'
    }

def run(protocol):
    well_96startx = 1 #index from 1 (as labelled on plate)
    well_96starty = "A" #letter of row in 96well plate, need quotes
    num_samples = 2
    dilution = 10 #1 in this dilution factor

    strobe(12, 8, True, protocol)
    setup(well_96startx, well_96starty, num_samples, protocol)
    titrate_together(dilution, protocol)
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

def setup(well_96startx, well_96starty, num_samples, protocol):
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

    global start_96wellx, start_96welly, samples
    start_96wellx = well_96startx-1
    row_dict = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7}
    start_96welly = row_dict[well_96starty]
    samples = num_samples

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

def pickup_tips(number, pipette, protocol):
    global tip300, tip20

    if pipette == p20m:
        if (tip20 % number) != 0:
            while (tip20 % 8) != 0:
                tip20 += 1
        tip20 += number-1
        p20m.pick_up_tip(tips20[which_tips20[tip20]])
        tip20 += 1    
    elif pipette == p300m:
        if (tip300 % number) != 0:
            while (tip300 % 8) != 0:
                tip300 += 1
        tip300 += number-1
        p300m.pick_up_tip(tips300[which_tips300[tip300]])
        tip300 += 1

def titrate_together(dilution, protocol):
    enzy_col = start_96wellx
    buff_col = enzy_col+1
    samp_col = buff_col+1
    
    #add buff
    pickup_tips(samples, p300m, protocol)
    p300m.aspirate(175, plate96.rows()[start_96welly][buff_col])
    for i in range(1,7):
        p300m.dispense(20, temp_pcr.rows()[0][i])
    p300m.blow_out(location=trash)

    #titrate
    p300m.aspirate(20+(20/dilution), plate96.rows()[start_96welly][enzy_col])
    p300m.dispense(20+(20/dilution), temp_pcr.rows()[start_96welly][0])    
    p300m.drop_tip()
    pickup_tips(samples, p20m, protocol)
    for i in range(0,5):
        p20m.aspirate((20/dilution), temp_pcr.rows()[0][i])
        p20m.dispense((20/dilution), temp_pcr.rows()[0][i+1])
        p20m.mix(3,10)
    p20m.aspirate((20/dilution), temp_pcr.rows()[0][5])
    p20m.drop_tip()
