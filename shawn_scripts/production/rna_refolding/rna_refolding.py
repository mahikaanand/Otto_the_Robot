from opentrons import protocol_api
import time
import math

metadata = {
    'protocolName': 'RNA refolding',
    'author': 'Shawn Laursen',
    'description': '''Place 1.11x RNA in 100mM KCl, 50mM MES pH 6.0
                      in A1 of temp rack.
                      Place 50mM MgCl2 in A1 of RT rack.
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0
    rna_vol = 40
    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    refold(rna_vol, protocol)
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
    global trash, tips20, tips300, p20m, p300m, tempdeck, temp_24, rt_24
    trash = protocol.fixed_trash['A1']
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_24 = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')
    rt_24 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 6) 

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

def refold(rna_vol, protocol):
    global tip300, tip20
    # heat denature at 95C for 3min
    tempdeck.set_temperature(celsius=95)
    protocol.delay(minutes=3)

    # cool to 20C
    tempdeck.set_temperature(celsius=20)

    # add 1/10 vol 50mM MgCl2
    mg_vol = rna_vol/10
    if mg_vol < 20:
        p20m.pick_up_tip(tips20[which_tips20[tip20]])
        tip20 += 1
        p20m.aspirate(mg_vol, rt_24.rows()[0][0])
        p20m.dispense(mg_vol, temp_24.rows()[0][0])
        if rna_vol < 40:
            p20m.mix(5,rna_vol/2)
        else:
            p20m.mix(5,20)
        p20m.drop_tip()
    else:
        p300m.pick_up_tip(tips300[which_tips300[tip300]])
        tip300 += 1
        p300m.aspirate(mg_vol, rt_24.rows()[0][0])
        p300m.dispense(mg_vol, temp_24.rows()[0][0])
        if rna_vol < 600:
            p20m.mix(5,rna_vol/2)
        else:
            p20m.mix(5,300)
        p300m.drop_tip()

    # incubate at 37C for 10min
    tempdeck.set_temperature(celsius=37)
    protocol.delay(minutes=10)

    # deactive heat
    tempdeck.deactivate()
