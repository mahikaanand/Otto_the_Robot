from opentrons import protocol_api
import time,math


metadata = {
    'protocolName': 'IVT assay',
    'author': 'Shawn Laursen',
    'description': '''You put mixes in 96 well plate: 
                        - 30ul 2x protein in col 0
                        - 100ul buffer in col 1 
                        - 60ul of DNA template in col 2
                        - 100ul ivt rxn (sans DNA temp) in col 3
                        - 20ul of DNase in col 4

                      Robot:
                        - Titrate 2x enzymes in pcr tubes 1:1 6 times, leaving #7 as control (10ul)
                        - Add DNA temp (5ul)
                        - Add ivt rxn (15ul) 
                        - Heat block to 37C
                        - Incubate at 37C for 30mins
                        - Add DNase (1ul)
                        - Incubate at 37C for 15mins''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0
    samples = 1
    
    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    ivt(samples, protocol)
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
    global tips20, tips300, p20m, p300m, plate96, tempdeck, temp_pcr
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

def ivt(samples, protocol):
    enzy_col = start_96well
    buff_col = enzy_col+1
    temp_col = buff_col+1
    rxnm_col = temp_col+1
    dnase_col = rxnm_col+1
    urea_col = dnase_col+1

    #add buffer
    pickup_tips(samples, p300m, protocol)
    p300m.distribute(10, plate96.rows()[0][buff_col],
                     temp_pcr.rows()[0][1:7],
                     disposal_volume=10, new_tip='never')
    p300m.transfer(21, plate96.rows()[0][buff_col],
                     temp_pcr.rows()[0][7],
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()

    #titrate enzymes
    pickup_tips(samples, p20m, protocol)
    p20m.transfer(20, plate96.rows()[0][enzy_col],
                   temp_pcr.rows()[0][0], new_tip='never')
    p20m.transfer(10, temp_pcr.rows()[0][0:5],
                   temp_pcr.rows()[0][1:6],
                   mix_after=(3, 10), new_tip='never')
    p20m.aspirate(10, temp_pcr.rows()[0][5])
    p20m.drop_tip()

    #add nucleic acid
    for i in range(0,8):
        pickup_tips(samples, p20m, protocol)
        p20m.transfer(5, plate96.rows()[0][temp_col],
                        temp_pcr.rows()[0][i],
                        disposal_volume=0, new_tip='never', 
                        mix_after=(3,10))
        p20m.drop_tip()
    
    #add ivt rxn mix
    for i in range(0,7):
        pickup_tips(samples, p20m, protocol)
        p20m.transfer(15, plate96.rows()[0][rxnm_col],
                        temp_pcr.rows()[0][i],
                        disposal_volume=0, new_tip='never', 
                        mix_after=(3,10))
        p20m.drop_tip()
    
    #incubate 30mins at 37C
    tempdeck.set_temperature(celsius=37)
    protocol.delay(minutes=30)

    #add dnase buff to samples
    for i in range(0,7):
        pickup_tips(samples, p20m, protocol)
        p20m.transfer(1, plate96.rows()[0][dnase_col],
                        temp_pcr.rows()[0][i],
                        disposal_volume=0, new_tip='never', 
                        mix_after=(3,10))
        p20m.drop_tip()

    #heat DNase for 15 mins
    protocol.delay(minutes=15)
    tempdeck.deactivate()
