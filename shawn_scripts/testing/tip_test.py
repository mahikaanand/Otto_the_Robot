from opentrons import protocol_api
import time

metadata = {
    'protocolName': 'tip test',
    'author': 'Shawn Laursen',
    'description': '''This protocol will make 32x12well dilutions in a 384 well
                      plate. The dilutions are 1:1 across the the plate and
                      leave the last well of each dilution with buffer (DNA)
                      only. It will take the even columns of a 96 well plate to
                      fill well 1 of each dilution and the adjacent well in the
                      96 well plate will provide the dilution buffer for the
                      other 11 wells of each dilution.''',
    'apiLevel': '2.8'
    }

def run(protocol: protocol_api.ProtocolContext):

    #turn on robot rail lights
    i = 0
    while i < 5:
        protocol.set_rail_lights(True)
        time.sleep(0.25)
        protocol.set_rail_lights(False)
        time.sleep(0.25)
        i += 1
    protocol.set_rail_lights(True)
    
    #setup
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 2)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])
    p300m.flow_rate.aspirate = 5
    p300m.flow_rate.dispense = 5

    p20m.pick_up_tip(tips20['H2'])
    p20m.aspirate(20, plate384.rows()[1][22])
    p20m.drop_tip()

    #turn off robot rail lights
    protocol.set_rail_lights(False)
