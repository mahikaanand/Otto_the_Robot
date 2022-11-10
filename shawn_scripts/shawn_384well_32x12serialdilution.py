from opentrons import protocol_api
import time

metadata = {
    'protocolName': '384 well plate, 32x12 1:1 Serial Dilution',
    'author': 'Shawn Laursen',
    'description': '''This protocol will make 32x12well dilutions in a 384 
well
                      plate. The dilutions are 1:1 across the the plate 
and
                      leave the last well of each dilution with buffer 
(DNA)
                      only. It will take the even columns of a 96 well 
plate to
                      fill well 1 of each dilution and the adjacent well 
in the
                      96 well plate will provide the dilution buffer for 
the
                      other 11 wells of each dilution.''',
    'apiLevel': '2.8'
    }

def run(protocol: protocol_api.ProtocolContext):

    #turn on robot rail lights
    i = 0
    while i < 10:
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

    #add 40ul of 50uM protein/20nM DNA from row 1,3,5,7 of 96well to 
384well
    p300m.transfer(40, plate96.rows()[0][0].bottom(1.75), 
plate384.rows()[0][0])
    p300m.transfer(40, plate96.rows()[0][2].bottom(1.75), 
plate384.rows()[1][0])
    p300m.transfer(40, plate96.rows()[0][4].bottom(1.75),
                   plate384.rows()[0][12])
    p300m.transfer(40, plate96.rows()[0][6].bottom(1.75),
                   plate384.rows()[1][12])

    p300m.flow_rate.dispense = 10

    #add 20ul of 1x DNA from row 2,4,6,8 of 96well to rest of 384well
    p300m.distribute(20, plate96.rows()[0][1].bottom(1.75),
                     plate384.rows()[0][1:12], disposal_volume=5)
    p300m.distribute(20, plate96.rows()[0][3].bottom(1.75),
                     plate384.rows()[1][1:12], disposal_volume=5)
    p300m.distribute(20, plate96.rows()[0][5].bottom(1.75),
                     plate384.rows()[0][13:24], disposal_volume=5)
    p300m.distribute(20, plate96.rows()[0][7].bottom(1.75),
                     plate384.rows()[1][13:24], disposal_volume=5)

    p20m.flow_rate.aspirate = 5

    #1:1 serial dilution 20ul 1:1 from 1-11 in 384well
    p20m.transfer(20, plate384.rows()[0][0:10], plate384.rows()[0][1:11],
                  mix_after=(3, 20), new_tip='once')
    p20m.pick_up_tip()
    p20m.aspirate(20, plate384.rows()[0][10])
    p20m.drop_tip()
    p20m.transfer(20, plate384.rows()[1][0:10], plate384.rows()[1][1:11],
                  mix_after=(3, 20), new_tip='once')
    p20m.pick_up_tip()
    p20m.aspirate(20, plate384.rows()[1][10])
    p20m.drop_tip()
    p20m.transfer(20, plate384.rows()[0][12:22], 
plate384.rows()[0][13:23],
                  mix_after=(3, 20), new_tip='once')
    p20m.pick_up_tip()
    p20m.aspirate(20, plate384.rows()[0][22])
    p20m.drop_tip()
    p20m.transfer(20, plate384.rows()[1][12:22], 
plate384.rows()[1][13:23],
                  mix_after=(3, 20), new_tip='once')
    p20m.pick_up_tip()
    p20m.aspirate(20, plate384.rows()[1][22])
    p20m.drop_tip()

    #turn off robot rail lights
    protocol.set_rail_lights(False)
