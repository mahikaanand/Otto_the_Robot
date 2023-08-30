from opentrons import protocol_api
import time
import sys


metadata = {
    'protocolName': 'test_96well',
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
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 5)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])
    p20m.pick_up_tip()
    p20m.transfer(20, plate96.rows()[0][0], plate96.rows()[0][5], 
                   new_tip='never')
    p20m.transfer(20, plate96.rows()[0][11].bottom(1.75), plate96.rows()[0][7], 
                       new_tip='never')
