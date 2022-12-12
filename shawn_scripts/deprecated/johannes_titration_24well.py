from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Johannes titration - 24 well',
    'author': 'Shawn Laursen',
    'description': '''Titrates buffer from trough 24x in 384well.
                      Put sample in first column, buffer in first well of trough
                      manually.''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(2, protocol)
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

def setup(num_buffs, protocol):
    #equiptment
    global tips300, tips300_2, trough, plate384, p300m, tempdeck
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    tempdeck = protocol.load_module('temperature module gen2', 10)

    global temp_buffs
    temp_buffs = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')

    #buffs
    global buffs, buffa, buffb, buffc, buffd
    buffa = "a"
    buffb = "b"
    buffc = "c"
    buffd = "d"
    buffs = [buffa, buffb, buffc, buffd]
    del buffs[num_buffs:]

    #single tips
    global which_tips, tip
    which_tips = []
    tip = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

    #single tips
    global which_compounds, compound
    which_compounds = []
    compound = 0
    comp_row_list = ['A','B','C','D']
    for row in comp_row_list:
        for i in range(1,7):
            which_compounds.append(row+str(i))

    #tip columns
    global which_tip_col, tip_col
    which_tip_col = []
    tip_col = 0
    for i in range(1,13):
        which_tip_col.append('A'+str(i))

def protein_titration(buff, protocol):
    global tip, compound, tip_col

    start_384well = 0
    if (buffs.index(buff) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    p300m.pick_up_tip(tips300_2[which_tip_col[tip_col]])
    tip_col += 1
    p300m.distribute(20, trough.wells()[0],
                     plate384.rows()[which_rows][start_384well+1:start_384well+24],
                     disposal_volume=20, new_tip='never')
    p300m.blow_out()
    p300m.transfer(30,
                   plate384.rows()[which_rows][start_384well:start_384well+21],
                   plate384.rows()[which_rows][start_384well+1:start_384well+22],
                   mix_after=(3, 20), new_tip='never')
    p300m.blow_out()
    p300m.aspirate(30, plate384.rows()[which_rows][start_384well+21])
    p300m.drop_tip()

    for i in range(which_rows, which_rows+16, 2):
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        p300m.aspirate(250, temp_buffs.wells_by_name()[which_compounds[compound]].bottom(-2))
        compound += 1
        for j in range(0,24):
            p300m.dispense(10, plate384.rows()[i][j].top())
        p300m.blow_out()
        p300m.drop_tip()
