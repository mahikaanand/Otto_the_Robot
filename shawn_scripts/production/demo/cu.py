from opentrons import protocol_api
import time,math


metadata = {
    'protocolName': 'Demonstration',
    'author': 'Shawn Laursen',
    'description': '''You put mixes in 96 well plate: 
                        - dye in col 0 of trough
                        - 1M NaOH in col 1 of trough
                        - more dye in 25ml falcon''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(protocol)
    make_cu(protocol)
    add_base(protocol)
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

def setup(protocol):
    #equiptment
    global tips300, p300m, plate96, trough, tubes
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 5)
    trough = protocol.load_labware('nest_12_reservoir_15ml', 6)
    tubes = protocol.load_labware('opentrons_6_tuberack_falcon_50ml_conical', 8)

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

def make_cu(protocol):
    pickup_tips(4, p300m, protocol)
    p300m.aspirate(200, trough.wells()[0])
    p300m.dispense(50, plate96.rows()[2][1])
    p300m.dispense(50, plate96.rows()[2][6])
    p300m.dispense(50, plate96.rows()[2][10])
    p300m.drop_tip()

    pickup_tips(1, p300m, protocol)
    p300m.aspirate(300, trough.wells()[0])
    p300m.dispense(50, plate96.rows()[1][2])
    p300m.dispense(50, plate96.rows()[1][3])
    p300m.dispense(50, plate96.rows()[1][4])
    p300m.dispense(50, plate96.rows()[6][2])
    p300m.dispense(50, plate96.rows()[6][3])
    p300m.dispense(25, plate96.rows()[6][4])
    p300m.blow_out(tubes.rows()[0][0])
    p300m.aspirate(300, tubes.rows()[0][0].top(-50))
    p300m.dispense(25, plate96.rows()[6][4])
    p300m.dispense(50, plate96.rows()[1][6])
    p300m.dispense(50, plate96.rows()[1][10])
    p300m.dispense(50, plate96.rows()[6][7])
    p300m.dispense(50, plate96.rows()[6][8])
    p300m.dispense(50, plate96.rows()[6][9])
    p300m.drop_tip()

def add_base(protocol):
    pickup_tips(8, p300m, protocol)
    p300m.distribute(50, trough.wells()[1], plate96.rows()[0][0:12],
                     new_tip='never')
    p300m.drop_tip()