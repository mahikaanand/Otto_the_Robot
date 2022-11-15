from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Tip rack check',
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
                                     tip_racks=[tips300_2])
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

    protocol.set_rail_lights(True)

    p300m.pick_up_tip(tips300['H1'])
    p300m.aspirate(100, temp_buffs.rows()[0][3].bottom(-1.5))
    p300m.blow_out(temp_buffs.rows()[0][3])
    p300m.aspirate(100, temp_buffs.rows()[0][4].bottom(-2))
    p300m.blow_out(temp_buffs.rows()[0][4])
    p300m.aspirate(100, temp_buffs.rows()[0][5].bottom(-2.5))
    p300m.blow_out(temp_buffs.rows()[0][5])
    p300m.aspirate(100, temp_buffs.rows()[0][2].bottom(-3))
    p300m.drop_tip()

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

