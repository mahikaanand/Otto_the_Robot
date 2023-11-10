from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Crosslinker titration',
    'author': 'Shawn Laursen',
    'description': '''This protocol will do a 7 well titration of crosslinker
                      (like BS3) from a stock with 1:3 (1 in 4)
                      dilutions, add set amount of protein to each well and
                      quench 30mins later.
                      Advised to spin down plate to mix after plating.
                      Advised to spin down plate after quenching.

                      Col0: 90ul XL
                      Col1: 30ul protein
                      Col2: 300ul buff
                      Col3: 300ul buff
                      Trough0: Glycine

                      Puts 60ul buffer in pcr strips from trough (no Tris,
                      glycine, or DTT).
                      Adds 80ul high concentration crosslinker (ex 5mM) from
                      column 1 of 96 well to pcr strip and titrates 6 times with
                      20ul (1:3), leaving last well as control.
                      Adds 10ul of protein (ex 5uM) from column 2 of 96 well
                      plate to all wells of stips.
                      Waits until 30min has elapsed from start of addition of
                      protein and adds 10ul of glycine from trough to each well.
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0
    quench_time = 0.5 #in minutes

    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    xl_titration(protocol)
    quench(quench_time, protocol)
    add_sample_buff(protocol)
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

def setup(well_96start, protocol):
    #equiptment
    global tips300, tips300_2, trough, p300m, plate96, tempdeck, temp_pcr
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300_2])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul')

    global glycine
    glycine = trough.wells()[0]

    global start_96well
    start_96well = well_96start

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
        if tip300 < 96:
            p300m.pick_up_tip(tips300[which_tips300[tip300]])
        else:
            p300m.pick_up_tip(tips300_2[which_tips300[tip300-96]])
        tip300 += 1

def xl_titration(protocol):
    xl_col = start_96well
    prot_col = xl_col+1
    buff_col = xl_col+2
    buff_col1 = xl_col+3

    pickup_tips(8, p300m, protocol)
    p300m.distribute(60, plate96.rows()[0][buff_col],
                     temp_pcr.rows()[0][1:4],
                     disposal_volume=0, new_tip='never')
    p300m.distribute(60, plate96.rows()[0][buff_col1],
                     temp_pcr.rows()[0][4:8],
                     disposal_volume=0, new_tip='never')
    p300m.transfer(80, plate96.rows()[0][xl_col],
                   temp_pcr.rows()[0][0], new_tip='never')
    p300m.transfer(20,
                   temp_pcr.rows()[0][0:5],
                   temp_pcr.rows()[0][1:6],
                   mix_after=(3,20), new_tip='never')
    p300m.aspirate(20, temp_pcr.rows()[0][5])
    p300m.drop_tip()

    global start_time
    start_time = time.time()

    pickup_tips(8, p300m, protocol)
    p300m.aspirate(80, plate96.rows()[0][prot_col])
    for j in range(0,7):
        p300m.dispense(10, temp_pcr.rows()[0][j].top())
        p300m.touch_tip()
    p300m.drop_tip()


def quench(wait_mins, protocol):
    end_time = start_time + wait_mins*60
    try:
        if not protocol.is_simulating():
            while time.time() < end_time:
                time.sleep(1)
        else:
            print('Not waiting, simulating')
    except KeyboardInterrupt:
        pass
        print()

    pickup_tips(8, p300m, protocol)
    p300m.aspirate(80, glycine)
    for j in range(0,7):
        p300m.dispense(10, temp_pcr.rows()[0][j].top())
        p300m.touch_tip()
    p300m.drop_tip()

def add_sample_buff(protocol):   
    sample_buff = start_96well+4
    sample_buff1 = start_96well+5
    for col in range(0,4):
        pickup_tips(8, p300m, protocol)
        p300m.aspirate(70, plate96.rows()[0][sample_buff])
        p300m.dispense(70, temp_pcr.rows()[0][col])
        p300m.mix(3,70)
        p300m.drop_tip()
    for col in range(4,8):
        pickup_tips(8, p300m, protocol)
        p300m.aspirate(70, plate96.rows()[0][sample_buff1])
        p300m.dispense(70, temp_pcr.rows()[0][col])
        p300m.mix(3,70)
        p300m.drop_tip()

def denature(protocol):
    tempdeck.set_temperature(celsius=95)
    protocol.delay(minutes=3)
    tempdeck.deactivate()
