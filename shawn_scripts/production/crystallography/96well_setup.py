from opentrons import protocol_api
import time
import math


metadata = {
    'protocolName': 'Crystallography - set up 96 well',
    'author': 'Shawn Laursen',
    'description': '''Makes 4 x 24 screen in 96 well block.
                      Makes 900ul of each.
                      Uses buffs from trough.
                      Each screen gets 4 buffs:
                        - 10x buff in 1
                        - 4x 1D (salt)
                        - 4x 2D (precip)
                        - 4x static (other)
                      Water in next well after buffs
                      Protocol (for loop each buff)
                        - 1x buffer in all wells
                        - correct amount of water in each
                        - 1D amounts
                        - 2D amounts
                        - Add 1x static''',
    'apiLevel': '2.11'
    }

def run(protocol):
    strobe(12, 8, True, protocol)
    setup(4, protocol)
    for buff in buffs:
        def_xy(buff, protocol)
        add_buff(buff, protocol)
        add_1d(buff, protocol)
        add_2d(buff, protocol)
        add_water(buff, protocol)
        add_static(buff, protocol)
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
    global trough, trough2, water, tips300, plate96, p300m
    trough = protocol.load_labware('nest_12_reservoir_15ml', 4)
    trough2 = protocol.load_labware('nest_12_reservoir_15ml', 1)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    plate96 = protocol.load_labware('thermoscientificnunc_96_wellplate_2000ul', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])

    #buffs
    global buffs, buffa, buffb, buffc, buffd, water
    buffa = [trough.wells()[0],trough.wells()[1],trough.wells()[2],trough.wells()[3]]
    buffb = [trough.wells()[4],trough.wells()[5],trough.wells()[6],trough.wells()[7]]
    buffc = [trough.wells()[8],trough.wells()[9],trough.wells()[10],trough.wells()[11]]
    buffd = [trough2.wells()[0],trough2.wells()[1],trough2.wells()[2],trough2.wells()[3]]
    buffs = [buffa, buffb, buffc, buffd]
    water = trough2.wells()[4]
    del buffs[num_buffs:]

    #single tips
    global which_tips, tip
    which_tips = []
    tip = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

def def_xy(buff,protocol):
    global buffx, buffy
    buff_num = buffs.index(buff)
    if buff_num == 0:
        buffx = 0
        buffy = 0
    elif buff_num == 1:
        buffx = 4
        buffy = 0
    elif buff_num == 2:
        buffx = 0
        buffy = 6
    elif buff_num == 3:
        buffx = 4
        buffy = 6

def add_buff(buff, protocol):
    global tip

    while (tip % 4) != 0:
        tip += 1
    tip += 3
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for col in range(0,6):
        p300m.aspirate(100, buff[0])
        p300m.dispense(100, plate96.rows()[buffx][buffy+col].top())  
        p300m.touch_tip()  
    p300m.drop_tip()

def add_1d(buff, protocol):
    global tip

    while (tip % 4) != 0:
        tip += 1
    tip += 3
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    vol = 300
    for col in range(0,6):
        p300m.aspirate(vol, buff[1])
        p300m.dispense(vol, plate96.rows()[buffx][buffy+col].top())  
        p300m.touch_tip()  
        vol -= 50
    p300m.drop_tip()

def add_2d(buff, protocol):
    global tip

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for i in range(0,4):
        vol = (3-i)*100
        for col in range(0,6):
            p300m.aspirate(vol, buff[2])
            p300m.dispense(vol, plate96.rows()[buffx+i][buffy+col].top())  
            p300m.touch_tip()        
    p300m.drop_tip()

def add_water(buff, protocol):
    global tip 

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for i in range(0,4):
        vol = i*100
        for col in range(0,6):
            if vol > 300:
                p300m.aspirate(300, water)
                p300m.dispense(300, plate96.rows()[buffx+i][buffy+col].top())  
                p300m.touch_tip() 
                p300m.aspirate(vol-300, water)
                p300m.dispense(vol-300, plate96.rows()[buffx+i][buffy+col].top())  
                p300m.touch_tip() 
            else:  
                p300m.aspirate(vol, water)
                p300m.dispense(vol, plate96.rows()[buffx+i][buffy+col].top())  
                p300m.touch_tip()   
            vol += 50         
    p300m.drop_tip()

def add_static(buff, protocol):
    global tip

    while (tip % 4) != 0:
        tip += 1
    tip += 3
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    for col in range(0,6):
        p300m.aspirate(300, buff[3])
        p300m.dispense(300, plate96.rows()[buffx][buffy+col].top())  
        p300m.touch_tip()  
    p300m.drop_tip()