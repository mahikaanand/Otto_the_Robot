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
    global tips300, trough, plate384, p300m, tempdeck
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
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

def protein_titration(buff, protocol):
    prot_col = buffs.index(buff)*3
    buff_col = prot_col+1
    extra_buff_col = buff_col+1
    start_384well = 0
    if (buffs.index(buff) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1
    p300m.pick_up_tip()
    p300m.distribute(20, trough.wells()[0],
                     plate384.rows()[which_rows][start_384well+1:start_384well+24],
                     disposal_volume=0, new_tip='never')
    p300m.blow_out()
    p300m.transfer(30,
                   plate384.rows()[which_rows][start_384well:start_384well+21],
                   plate384.rows()[which_rows][start_384well+1:start_384well+22],
                   mix_after=(3, 20), new_tip='never')
    p300m.blow_out()
    p300m.aspirate(30, plate384.rows()[which_rows][start_384well+21])
    p300m.drop_tip()
