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

                      Puts 60ul buffer in 384 well plate from trough (no Tris,
                      glycine, or DTT).
                      Adds 80ul high concentration crosslinker (ex 5mM) from
                      column 1 of 96 well to 384 well and titrates 6 times with
                      20ul (1:3), leaving last well as control.
                      Adds 10ul of protein (ex 5uM) from column 2 of 96 well
                      plate to all wells of 384 well.
                      Waits until 30min has elapsed from start of addition of
                      protein and adds 10ul of glycine from trough to each well.
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
        xl_titration(buff, protocol)
    for buff in buffs:
        quench(buff, quench_time, protocol)
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
    global tips300, trough, plate384, p300m, plate96
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)

    global glycine
    glycine = trough.wells()[0]

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

def xl_titration(buff, protocol):
    xl_col = (buffs.index(buff)*2)+start_96well
    prot_col = xl_col+1
    buff_col = xl_col+2
    buff_col1 = xl_col+3

    if ((buffs.index(buff)+start_quad) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    if (buffs.index(buff) + start_quad) < 2:
        start_384well = 0
    else:
        start_384well = 12

    p300m.pick_up_tip()
    p300m.distribute(60, plate96.rows()[0][buff_col],
                     plate384.rows()[which_rows][start_384well+1:start_384well+4],
                     disposal_volume=0, new_tip='never')
    p300m.distribute(60, plate96.rows()[0][buff_col1],
                     plate384.rows()[which_rows][start_384well+4:start_384well+7],
                     disposal_volume=0, new_tip='never')
    p300m.blow_out()
    p300m.transfer(80, plate96.rows()[0][xl_col],
                   plate384.rows()[which_rows][start_384well], new_tip='never')
    p300m.blow_out()
    p300m.transfer(20,
                   plate384.rows()[which_rows][start_384well:start_384well+5],
                   plate384.rows()[which_rows][start_384well+1:start_384well+6],
                   mix_after=(3, 20), new_tip='never')
    p300m.blow_out()
    p300m.aspirate(20, plate384.rows()[which_rows][start_384well+5])
    p300m.drop_tip()

    global start_times
    start_times.append(time.time())

    p300m.pick_up_tip()
    p300m.aspirate(80, plate96.rows()[0][prot_col])
    for j in range(start_384well, start_384well+7):
        p300m.dispense(10, plate384.rows()[which_rows][j].top())
        p300m.touch_tip()
    p300m.drop_tip()


def quench(buff, wait_mins, protocol):
    if ((buffs.index(buff)+ start_quad) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    if (buffs.index(buff) + start_quad) < 2:
        start_384well = 0
    else:
        start_384well = 12

    end_time = start_times[buffs.index(buff)] + wait_mins*60

    try:
        if not protocol.is_simulating():
            while time.time() < end_time:
                time.sleep(1)
        else:
            print('Not waiting, simulating')
    except KeyboardInterrupt:
        pass
        print()

    p300m.pick_up_tip()
    p300m.aspirate(80, glycine)
    for j in range(start_384well, start_384well+7):
        p300m.dispense(10, plate384.rows()[which_rows][j].top())
        p300m.touch_tip()
    p300m.drop_tip()
