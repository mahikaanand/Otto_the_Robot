from opentrons import protocol_api
import time


metadata = {
    'protocolName': 'Nuclease - titration for overweekend (part 1)',
    'author': 'Shawn Laursen',
    'description': '''You put mixes in 96 well plate: 
                        - 30ul 2x protein+RNA in col 0
                        - 100ul RNA in col 1 

                      Robot:
                        - Titrate protein in pcr tubes 1:1 6 times, leaving #7 as control (10ul)''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0

    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    titrate(protocol)
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

def setup(well_96start, protocol):
    #equiptment
    global tips20, tips201, tips300, p20m, p300m, plate96, tempdeck, temp_pcr
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips201 = protocol.load_labware('opentrons_96_tiprack_20ul', 1)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20, tips201])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul')

    global start_96well
    start_96well = well_96start

def titrate(protocol):
    enzy_col = start_96well
    buff_col = enzy_col+1
    samp_col = buff_col+1
    sdsb_col = samp_col+1
    form_col = sdsb_col+1

    #add buffer
    p300m.pick_up_tip()
    p300m.distribute(10, plate96.rows()[0][buff_col],
                     temp_pcr.rows()[0][1:7],
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()

    #titrate enzymes
    p20m.pick_up_tip()
    p20m.transfer(20, plate96.rows()[0][enzy_col],
                   temp_pcr.rows()[0][0], new_tip='never')
    p20m.transfer(10, temp_pcr.rows()[0][0:5],
                   temp_pcr.rows()[0][1:6],
                   mix_after=(3, 10), new_tip='never')
    p20m.aspirate(10, temp_pcr.rows()[0][5])
    p20m.drop_tip()

    #add nucleic acid
    p20m.transfer(10, plate96.rows()[0][samp_col],
                     temp_pcr.rows()[0][0:7],
                     disposal_volume=0, new_tip='always', 
                     mix_after=(3,10))
