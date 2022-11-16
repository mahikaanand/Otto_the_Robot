from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Fast Salt screen 4x7x12 1:1 Serial Dilutions',
    'author': 'Shawn Laursen',
    'description': '''This protocol will dilute buffer and protein stocks in 96
                      well, making 4(pH)x7(salt) conditions. You will need 16
                      inputs: protien+DNA+salt, salt+DNA, protein+DNA, DNA (for
                      each pH). The program will dilute each column of the 96
                      well and combine the exta DNA columns with the even
                      columns to make 250ul for each dilution. It will then make
                      32x12well dilutions in a 384 well plate using the odd
                      columns for high protein. The dilutions are 1:1 across the
                      the plate and leave the last well of each dilution with
                      buffer (DNA) only. Control at bottom of each column.''',
    'apiLevel': '2.8'
    }

def run(protocol):
    #setup
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300_2])
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_buffs = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')
    equiptment = [tips300, tips300_2, plate96, plate384, p300m, tempdeck,
                  trough]

    buffa = trough.wells()[0]
    buffb = trough.wells()[1]
    buffc = trough.wells()[2]
    buffd = trough.wells()[3]
    high_salt = trough.wells()[4]
    low_salt = trough.wells()[5]
    edta = trough.wells()[6]
    water = trough.wells()[7]
    general_buffs = [edta, high_salt, low_salt, water, temp_buffs]
    buffs = [buffa, buffb, buffc, buffd]

    tip_row_list = ['H','G','F','E','D','C','B','A']
    which_tips = []
    for i in range(0,96):
        which_tips.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))
    tip = 0

    #turn on robot rail lights
    strobe(5, 8, protocol)

    #make buffs
    tip = make_buffs(protocol, equiptment, general_buffs, buffs, True,
                     which_tips, tip)

    #transfer buffs to 96well
    tip = fill_96well(protocol, equiptment, which_tips, tip, buffs, temp_buffs)

    #titrate salt
    tip = titrate_salt(protocol, equiptment, which_tips, tip)

    #do titration
    if len(buffs) == 1:
        titrate(1, 0, 0, 'odd', protocol, equiptment)
    elif len(buffs) == 2:
        titrate(1, 0, 0, 'odd', protocol, equiptment)
        titrate(3, 2, 0, 'even', protocol, equiptment)
    elif len(buffs) == 3:
        titrate(1, 0, 0, 'odd', protocol, equiptment)
        titrate(3, 2, 0, 'even', protocol, equiptment)
        titrate(5, 4, 12, 'odd', protocol, equiptment)
    elif len(buffs) == 4:
        titrate(1, 0, 0, 'odd', protocol, equiptment)
        titrate(3, 2, 0, 'even', protocol, equiptment)
        titrate(5, 4, 12, 'odd', protocol, equiptment)
        titrate(7, 6, 12, 'even', protocol, equiptment)

    #turn off robot rail lights
    strobe(5, 8, protocol)
    protocol.set_rail_lights(False)

def strobe(blinks, hz, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(True)

def titrate(buff_96col, protien_96col, start_384well, which_rows, protocol,
            equiptment):
    tips300, tips300_2, plate96 = equiptment[0], equiptment[1], equiptment[2]
    plate384, p300m = equiptment[3], equiptment[4]

    if which_rows == 'odd':
        which_rows = 0
    elif which_rows == 'even':
        which_rows = 1
    else:
        sys.exit('Wrong value for which_rows.')

    p300m.pick_up_tip()

    if buff_96col == 1:
        p300m.transfer(120, plate96.rows()[0][8].bottom(1.75),
                       plate96.rows()[0][1],
                       new_tip='never')
    elif buff_96col == 3:
        p300m.transfer(120, plate96.rows()[0][9].bottom(1.75),
                       plate96.rows()[0][3],
                       new_tip='never')
    elif buff_96col == 5:
        p300m.transfer(120, plate96.rows()[0][10].bottom(1.75),
                       plate96.rows()[0][5],
                       new_tip='never')
    elif buff_96col == 7:
        p300m.transfer(120, plate96.rows()[0][11].bottom(1.75),
                       plate96.rows()[0][7],
                       new_tip='never')

    if start_384well == 0:
        dest_wells = [11,10,9,8,7,6,5,4,3,2,1]
    elif start_384well == 12:
        dest_wells = [23,22,21,20,19,18,17,16,15,14,13]
    p300m.distribute(20, plate96.rows()[0][buff_96col].bottom(1.75),
                     plate384.rows()[which_rows][dest_wells],
                     disposal_volume=0, new_tip='never')
    p300m.flow_rate.aspirate = 25
    p300m.flow_rate.dispense = 25
    p300m.transfer(40, plate96.rows()[0][protien_96col].bottom(1.75),
                   plate384.rows()[which_rows][start_384well], new_tip='never')
    p300m.transfer(20,
                   plate384.rows()[which_rows][start_384well:start_384well+10],
                   plate384.rows()[which_rows][start_384well+1:start_384well+11],
                   mix_after=(3, 20), new_tip='never')
    p300m.aspirate(20, plate384.rows()[which_rows][start_384well+10])
    p300m.drop_tip()

def titrate_salt(protocol, equiptment, which_tips, tip):
    tips300, tips300_2, plate96 = equiptment[0], equiptment[1], equiptment[2]
    plate384, p300m = equiptment[3], equiptment[4]

    for column in range(0,12):
        if column in (0,2,4,6):
            p300m.pick_up_tip(tips300[which_tips[tip]])
            tip += 1
            for row in range(1,6):
                p300m.aspirate(50, plate96.rows()[row][column].bottom(1.75))
                p300m.dispense(50, plate96.rows()[row+1][column].bottom(1.75))
                p300m.mix(3,50)
            p300m.aspirate(50, plate96.rows()[6][column].bottom(1.75))
            p300m.drop_tip()
        else:
            p300m.pick_up_tip(tips300[which_tips[tip]])
            tip += 1
            for row in range(1,6):
                p300m.aspirate(125, plate96.rows()[row][column].bottom(1.75))
                p300m.dispense(125, plate96.rows()[row+1][column].bottom(1.75))
                p300m.mix(3,50)
            p300m.aspirate(125, plate96.rows()[6][column].bottom(1.75))
            p300m.drop_tip()
    return tip

def make_buffs(protocol, equiptment, general_buffs, buffs, make_high,
               which_tips, tip):
    tips300, tips300_2, plate96 = equiptment[0], equiptment[1], equiptment[2]
    plate384, p300m, tempdeck = equiptment[3], equiptment[4], equiptment[5]
    trough = equiptment[6]
    edta, high_salt = general_buffs[0], general_buffs[1]
    low_salt, water = general_buffs[2], general_buffs[3]
    temp_buffs = general_buffs[4]
    protein = temp_buffs.wells_by_name()['A1']
    dna = temp_buffs.wells_by_name()['A2']
    dna_extra = temp_buffs.wells_by_name()['D2']

    hi_prot_dna_vol = 150
    lo_prot_dna_vol = 350
    hi_dna_vol = 550
    lo_dna_vol = 1500

    hpdv1 = (hi_prot_dna_vol)/5
    lpdv1 = (lo_prot_dna_vol)/5
    hdv1 = (hi_dna_vol)/5
    ldv1 = (lo_dna_vol)/5

    #make high protein + DNA
    if make_high:
        #add edta
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((hpdv1+lpdv1+hdv1), edta)
                p300m.dispense(hpdv1, temp_buffs.rows()[0][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(hdv1, temp_buffs.rows()[2][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(edta)
                p300m.aspirate((ldv1), edta)
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(edta)
        p300m.drop_tip()

        #add high_salt
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((hpdv1+hdv1), high_salt)
                p300m.dispense(hpdv1, temp_buffs.rows()[0][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(hdv1, temp_buffs.rows()[2][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(high_salt)
        p300m.drop_tip()

        #add low_salt
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((lpdv1), low_salt)
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(low_salt)
                p300m.aspirate((ldv1), low_salt)
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(low_salt)
        p300m.drop_tip()

        #add water
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((hdv1), water)
                p300m.dispense(hdv1, temp_buffs.rows()[2][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(water)
                p300m.aspirate((ldv1), water)
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(water)
        p300m.drop_tip()

        #add protein
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((hpdv1+lpdv1), protein.bottom(-2))
                p300m.dispense(hpdv1, temp_buffs.rows()[0][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(protein)
        p300m.drop_tip()

        #add DNA
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((hpdv1+lpdv1+hdv1), dna.bottom(-2))
                p300m.dispense(hpdv1, temp_buffs.rows()[0][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(hdv1, temp_buffs.rows()[2][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(dna)
                p300m.aspirate((ldv1), dna_extra.bottom(-2))
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(dna_extra)
        p300m.drop_tip()

        #add buff
        for buff in range(0,len(buffs)):
                p300m.pick_up_tip(tips300[which_tips[tip]])
                tip += 1
                p300m.aspirate((hpdv1+lpdv1+hdv1), buffs[buff])
                p300m.dispense(hpdv1, temp_buffs.rows()[0][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.dispense(hdv1, temp_buffs.rows()[2][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(buffs[buff])
                p300m.aspirate((ldv1), buffs[buff])
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(buffs[buff])
                p300m.drop_tip()
    else:
        #add edta
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((lpdv1), edta)
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(edta)
                p300m.aspirate((ldv1), edta)
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(edta)
        p300m.drop_tip()

        #add low_salt
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((lpdv1), low_salt)
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(low_salt)
                p300m.aspirate((ldv1), low_salt)
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(low_salt)
        p300m.drop_tip()

        #add water
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((ldv1), water)
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(water)
        p300m.drop_tip()

        #add protein
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((lpdv1), protein.bottom(-2))
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(protein)
        p300m.drop_tip()

        #add DNA
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        for buff in range(0,len(buffs)):
                p300m.aspirate((lpdv1), dna.bottom(-2))
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(dna)
                p300m.aspirate((ldv1), dna_extra.bottom(-2))
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(dna_extra)
        p300m.drop_tip()

        #add buff
        for buff in range(0,len(buffs)):
                p300m.pick_up_tip(tips300[which_tips[tip]])
                tip += 1
                p300m.aspirate((lpdv1), buffs[buff])
                p300m.dispense(lpdv1, temp_buffs.rows()[1][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(buffs[buff])
                p300m.aspirate((ldv1), buffs[buff])
                p300m.dispense(ldv1, temp_buffs.rows()[3][buff+2].top())
                p300m.touch_tip()
                p300m.blow_out(buffs[buff])
    return tip

def fill_96well(protocol, equiptment, which_tips, tip, buffs, temp_buffs):
    tips300, tips300_2, plate96 = equiptment[0], equiptment[1], equiptment[2]
    plate384, p300m, tempdeck = equiptment[3], equiptment[4], equiptment[5]

    #move protein wells
    column = 0
    for buff in range(0,len(buffs)):
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        p300m.mix(3,50, temp_buffs.rows()[0][buff+2])
        p300m.aspirate(100, temp_buffs.rows()[0][buff+2].bottom(-2))
        p300m.dispense(100, plate96.rows()[1][column].bottom(1.75))
        p300m.blow_out(plate96.rows()[1][column])
        p300m.drop_tip()

        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        p300m.mix(3,100, temp_buffs.rows()[1][buff+2])
        p300m.aspirate(300, temp_buffs.rows()[1][buff+2].bottom(-2))
        for row in range(2,8):
            p300m.dispense(50, plate96.rows()[row][column].bottom(1.75))
        p300m.blow_out(plate96.rows()[2][column])
        p300m.drop_tip()
        column += 2

    #move buff wells
    column = 1
    extra = 8
    for buff in range(0,len(buffs)):
        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        p300m.mix(3,250, temp_buffs.rows()[2][buff+2])
        p300m.aspirate(250, temp_buffs.rows()[2][buff+2].bottom(-2))
        p300m.dispense(250, plate96.rows()[1][column].bottom(1.75))
        p300m.blow_out(plate96.rows()[1][column])
        p300m.aspirate(250, temp_buffs.rows()[2][buff+2].bottom(-2))
        p300m.dispense(250, plate96.rows()[1][extra].bottom(1.75))
        p300m.blow_out(plate96.rows()[1][extra].bottom(1.75))
        p300m.drop_tip()

        p300m.pick_up_tip(tips300[which_tips[tip]])
        tip += 1
        p300m.mix(3,250, temp_buffs.rows()[3][buff+2])
        for row in range(2,8):
            p300m.aspirate(250, temp_buffs.rows()[3][buff+2].bottom(-2))
            p300m.dispense(125, plate96.rows()[row][column].bottom(1.75))
            p300m.dispense(125, plate96.rows()[row][extra].bottom(1.75))
            p300m.blow_out(plate96.rows()[row][extra])
        p300m.drop_tip()
        column += 2
        extra += 1

    #move controls
    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3,50, temp_buffs.rows()[1][0])
    p300m.aspirate(100, temp_buffs.rows()[1][0].bottom(-2))
    p300m.dispense(50, plate96.rows()[0][0].bottom(1.75))
    p300m.dispense(50, plate96.rows()[0][2].bottom(1.75))
    p300m.blow_out(temp_buffs.rows()[1][0])
    p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3,50, temp_buffs.rows()[2][0])
    p300m.aspirate(100, temp_buffs.rows()[2][0].bottom(-2))
    p300m.dispense(50, plate96.rows()[0][4].bottom(1.75))
    p300m.dispense(50, plate96.rows()[0][6].bottom(1.75))
    p300m.blow_out(temp_buffs.rows()[2][0])
    p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3,250, temp_buffs.rows()[1][1])
    p300m.aspirate(250, temp_buffs.rows()[1][1].bottom(-2))
    p300m.dispense(125, plate96.rows()[0][1].bottom(1.75))
    p300m.dispense(125, plate96.rows()[0][3].bottom(1.75))
    p300m.blow_out(temp_buffs.rows()[1][1])
    p300m.aspirate(250, temp_buffs.rows()[1][1].bottom(-2))
    p300m.dispense(125, plate96.rows()[0][8].bottom(1.75))
    p300m.dispense(125, plate96.rows()[0][9].bottom(1.75))
    p300m.blow_out(temp_buffs.rows()[1][1])
    p300m.drop_tip()

    p300m.pick_up_tip(tips300[which_tips[tip]])
    tip += 1
    p300m.mix(3,250, temp_buffs.rows()[2][1])
    p300m.aspirate(250, temp_buffs.rows()[2][1].bottom(-2))
    p300m.dispense(125, plate96.rows()[0][5].bottom(1.75))
    p300m.dispense(125, plate96.rows()[0][7].bottom(1.75))
    p300m.blow_out(temp_buffs.rows()[2][1])
    p300m.aspirate(250, temp_buffs.rows()[2][1].bottom(-2))
    p300m.dispense(125, plate96.rows()[0][10].bottom(1.75))
    p300m.dispense(125, plate96.rows()[0][11].bottom(1.75))
    p300m.blow_out(temp_buffs.rows()[2][1])
    p300m.drop_tip()

    return tip
