from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Protein crosslinking experiment - hetero',
    'author': 'Shawn Laursen',
    'description': '''This protocol will add set amount of protein to each well,
                      do a 7 well titration of a second protein from a stock with
                      1:3 (1 in 4) dilutions, then add crosslinker and quench
                      30mins later.
                      Advised to spin down plate to mix after plating.
                      Advised to spin down plate after quenching.

                      Puts 50ul buffer in 384 well plate from trough (no Tris,
                      glycine, or DTT).
                      Adds 10ul of stable protein to all wells from column 2 of
                      96 well.
                      Adds 80ul high concentration protein from
                      column 3 of 96 well to 384 well and titrates 7 times with
                      20ul (1:3), leaving last well as control.
                      Adds 10ul of crosslinker from  column 1 of 96 well plate
                      to all wells of 384 well.
                      Waits until 30min has elapsed from start of addition of
                      protein and adds 10ul of glycine from trough to each well.
                      ''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(1, 0, protocol)
    for buff in buffs:
        protein_titration(buff, protocol)
    for buff in buffs:
        quench(buff, 30, protocol)
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

def setup(num_buffs, well_start, protocol):
    #equiptment
    global tips300, trough, plate384, p300m, plate96
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)

    global buffer, glycine
    buffer = trough.wells()[0]
    glycine = trough.wells()[1]

    #buffs
    global buffs, buffa, buffb, buffc, buffd
    buffa = "a"
    buffb = "b"
    buffc = "c"
    buffd = "d"
    buffs = [buffa, buffb, buffc, buffd]
    del buffs[num_buffs:]

    global start_96well
    start_96well = well_start

    global start_times
    start_times = []

def protein_titration(buff, protocol):
    xl_col = (buffs.index(buff)*2)+start_96well
    prot_col = xl_col+1
    prot2_col = xl_col+2
    if (buffs.index(buff) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    if buffs.index(buff) < 2:
        start_384well = 0
    else:
        start_384well = 12

    p300m.pick_up_tip()
    p300m.distribute(50, buffer,
                     plate384.rows()[which_rows][start_384well+1:start_384well+7],
                     disposal_volume=0, new_tip='never')
    p300m.blow_out()
    p300m.aspirate(80, plate96.rows()[0][prot_col].bottom(1.75))
    for j in range(0,7):
        p300m.dispense(10, plate384.rows()[which_rows][j].top())
        p300m.touch_tip()
    p300m.drop_tip()

    p300m.pick_up_tip()
    p300m.transfer(80, plate96.rows()[0][prot2_col].bottom(1.75),
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
    p300m.aspirate(80, plate96.rows()[0][prot_col].bottom(1.75))
    for j in range(0,7):
        p300m.dispense(10, plate384.rows()[which_rows][j].top())
        p300m.touch_tip()
    p300m.drop_tip()


def quench(buff, wait_mins, protocol):
    if (buffs.index(buff) % 2) == 0:
        which_rows = 0
    else:
        which_rows = 1

    if buffs.index(buff) < 2:
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
    for j in range(0,7):
        p300m.dispense(10, plate384.rows()[which_rows][j].top())
        p300m.touch_tip()
    p300m.drop_tip()
