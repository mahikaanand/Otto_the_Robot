from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Prep crosslinker titration for gels',
    'author': 'Shawn Laursen',
    'description': '''This protocol will take the samples from the 7well 
                      crosslinking and:
                      - put them into pcr strips 
                      - add SB 
                      - heat denature samples

                      Need 300ul tips
                      PCR strips in heat block 
                      output of crosslinking protocol.
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    quad384 = 1 #up to 4 
    well_96start = 0 #index from 0
    quad_start = 0 #index from 0
    quench_time = 30 #in minutes

    strobe(12, 8, True, protocol)
    setup(quad384, well_96start, quad_start, protocol)
    for buff in buffs:
        transfer(buff, protocol)
    for buff in buffs:
        prep(buff, protocol)
    denature(protocol)
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

def setup(num_buffs, well_96start, quad_start, protocol):
    #equiptment
    global tips300, trough, plate384, p300m, plate96, tempdeck, temp_pcr, tubes24
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    tubes24 = protocol.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap', 11) 

    global glycine, sb
    glycine = trough.wells()[0]
    sb = tubes24.rows()[0][0]

    #buffs
    global buffs, buffa, buffb, buffc, buffd
    buffa = "a"
    buffb = "b"
    buffc = "c"
    buffd = "d"
    buffs = [buffa, buffb, buffc, buffd]
    del buffs[num_buffs:]

    global start_96well
    start_96well = well_96start

    global start_quad
    start_quad = quad_start

    global start_times
    start_times = []

    p300m.flow_rate.aspirate = 40
    p300m.flow_rate.dispense = 40

    #single tips
    global which_tips300, tip300
    which_tips300 = []
    tip300 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips300.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

def pickup_tips(number, pipette, protocol):
    global tip300
   
    if pipette == p300m:
        if (tip300 % number) != 0:
            while (tip300 % 8) != 0:
                tip300 += 1
        tip300 += number-1
        p300m.pick_up_tip(tips300[which_tips300[tip300]])
        tip300 += 1

def transfer(buff, protocol): 

    for row in range(0,16,2):    
        counter = 0
        for col in range(0,7):     
            pickup_tips(1, p300m, protocol)
            p300m.aspirate(80, plate384.rows()[row][col])
            p300m.dispense(80, temp_pcr.rows()[counter][col])
            counter += 1
            p300m.drop_tip()

def prep(buff, protocol):
    for row in range(0,7):
        for col in range(0,7):     
            pickup_tips(1, p300m, protocol)
            p300m.aspirate(80, sb)
            p300m.dispense(80, temp_pcr.rows()[row][col])
            p300m.mix(3,80)
            p300m.drop_tip()

def denature(protocol):
    tempdeck.set_temperature(celsius=95)
    protocol.delay(minutes=3)
    tempdeck.deactivate()
