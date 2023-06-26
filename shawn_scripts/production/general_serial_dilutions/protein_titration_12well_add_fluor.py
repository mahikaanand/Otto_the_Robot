from opentrons import protocol_api
import time
import sys
import math
import random
import subprocess


metadata = {
    'protocolName': 'Protein titration - 12 well, add fluor after',
    'author': 'Shawn Laursen',
    'description': '''You put mixes in 96 well plate: 
                        - 30ul of protein col 0 
                        - 150ul of dilutant col 1 
                        - 150ul of fluor col 2
                      Robot:
                        - Titrates protein 12 times in 384well 
                        - Add 10ul of fluor to all wells''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0

    strobe(12, 8, True, protocol)
    setup(4, well_96start, protocol)
    for buff in buffs:
        protein_titration(buff, protocol)
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

def setup(num_buffs, well_96start, protocol):
    #equiptment
    global tips20, plate96, plate384, p20m, p300m
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])

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

def protein_titration(buff, protocol):
    prot_col = (buffs.index(buff)*3)+start_96well
    buff_col = prot_col+1
    fluor_col = buff_col+1
    start_384well = 0
    if (buffs.index(buff) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    if buffs.index(buff) < 2:
        start_384well = 0
    else:
        start_384well = 12

    p300m.pick_up_tip()
    p300m.distribute(10, plate96.rows()[0][buff_col],
                     plate384.rows()[which_rows][start_384well+1:start_384well+12],
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()
    p20m.pick_up_tip()
    p20m.transfer(20, plate96.rows()[0][prot_col],
                   plate384.rows()[which_rows][start_384well], new_tip='never')
    p20m.transfer(10,
                   plate384.rows()[which_rows][start_384well:start_384well+10],
                   plate384.rows()[which_rows][start_384well+1:start_384well+11],
                   mix_after=(3, 10), new_tip='never')
    p20m.blow_out()
    p20m.aspirate(10, plate384.rows()[which_rows][start_384well+10])
    p20m.drop_tip()
    p300m.pick_up_tip()
    p300m.aspirate(130, plate96.rows()[0][fluor_col])
    for j in range(start_384well, start_384well+12):
        p300m.dispense(10, plate384.rows()[which_rows][j].top())
        p300m.touch_tip(radius=0.75, v_offset=0)
    p300m.drop_tip()
