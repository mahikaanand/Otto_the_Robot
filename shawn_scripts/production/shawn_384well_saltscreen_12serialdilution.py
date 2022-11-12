from opentrons import protocol_api
import time
import sys


metadata = {
    'protocolName': 'Salt screen 4x7x12 1:1 Serial Dilutions',
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
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    equiptment = [tips300, plate96, plate384, p300m]

    #turn on robot rail lights
    strobe(5, protocol)

    #titrate salt
    titrate_salt(protocol, equiptment)

    #do titration
    titrate(1, 0, 0, 'odd', protocol, equiptment)
    titrate(3, 2, 0, 'even', protocol, equiptment)
    titrate(5, 4, 12, 'odd', protocol, equiptment)
    titrate(7, 6, 12, 'even', protocol, equiptment)

    #turn off robot rail lights
    strobe(5, protocol)
    protocol.set_rail_lights(False)

def strobe(blinks, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(0.25)
        protocol.set_rail_lights(False)
        time.sleep(0.25)
        i += 1
    protocol.set_rail_lights(True)

def titrate(buff_96col, protien_96col, start_384well, which_rows, protocol, equiptment):
    tips300, plate96, plate384, p300m = equiptment[0], equiptment[1], equiptment[2], equiptment[3]

    if which_rows == 'odd':
        which_rows = 0
    elif which_rows == 'even':
        which_rows = 1
    else:
        sys.exit('Wrong value for which_rows.')

    p300m.flow_rate.aspirate = 5
    p300m.flow_rate.dispense = 10
    p300m.pick_up_tip()

    if buff_96col == 1:
        p300m.transfer(125, plate96.rows()[0][8].bottom(1.75), plate96.rows()[0][1], 
                       new_tip='never')
    elif buff_96col == 3:
        p300m.transfer(125, plate96.rows()[0][9].bottom(1.75), plate96.rows()[0][3], 
                       new_tip='never')
    elif buff_96col == 5:
        p300m.transfer(125, plate96.rows()[0][10].bottom(1.75), plate96.rows()[0][5], 
                       new_tip='never')
    elif buff_96col == 7:
        p300m.transfer(125, plate96.rows()[0][11].bottom(1.75), plate96.rows()[0][7], 
                       new_tip='never')

    p300m.distribute(20, plate96.rows()[0][buff_96col].bottom(1.75),
                     plate384.rows()[which_rows][start_384well+1:start_384well+12],
                     disposal_volume=5, new_tip='never')
    p300m.flow_rate.dispense = 5
    p300m.transfer(40, plate96.rows()[0][protien_96col].bottom(1.75),
                   plate384.rows()[which_rows][start_384well], new_tip='never')
    p300m.transfer(20, plate384.rows()[which_rows][start_384well:start_384well+10],
                   plate384.rows()[which_rows][start_384well+1:start_384well+11],
                   mix_after=(3, 20), new_tip='never')
    p300m.aspirate(20, plate384.rows()[which_rows][start_384well+10])
    p300m.drop_tip()

def titrate_salt(protocol, equiptment):
    tips300, plate96, plate384, p300m = equiptment[0], equiptment[1], equiptment[2], equiptment[3]
    p300m.flow_rate.aspirate = 5
    p300m.flow_rate.dispense = 5

    which_tips = ['H1','G1','F1','E1','D1','C1','B1','A1','H2','G2','F2','E2']
    for column in range(0,12):
        if column in (0,2,4,6):
            p300m.pick_up_tip(tips300[which_tips[column]])
            for row in range(0,6):
                p300m.aspirate(50, plate96.rows()[row][column].bottom(1.75))
                p300m.dispense(50, plate96.rows()[row+1][column].bottom(1.75))
                p300m.mix(3,50)
            p300m.aspirate(50, plate96.rows()[6][column].bottom(1.75))        
            p300m.drop_tip()
        else:
            p300m.pick_up_tip(tips300[which_tips[column]])
            for row in range(0,6):
                p300m.aspirate(125, plate96.rows()[row][column].bottom(1.75))
                p300m.dispense(125, plate96.rows()[row+1][column].bottom(1.75))
                p300m.mix(3,50)
            p300m.aspirate(125, plate96.rows()[6][column].bottom(1.75))        
            p300m.drop_tip()
