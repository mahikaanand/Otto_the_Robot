from opentrons import protocol_api
import time
import sys
import math
import random
import subprocess


metadata = {
    'protocolName': 'Nuclease assay',
    'author': 'Shawn Laursen',
    'description': '''You put mixes in 96 well plate: 
                        - 30ul 2x enzyme in col 0
                        - 100ul buffer in col 1 
                        - 100ul nucleic acid/protein in col 2
                        - 200ul SDS-urea buffer in col 3
                      Robot:
                        - Heat block to 37C
                        - Titrate 2x enzymes in pcr tubes 1:1 6 times, leaving #7 as control (10ul)
                        - Add 2x nucleic acid/protein stock (10ul) 
                        - Incubate at 37C for 15mins
                        - Add SDS buff to all wells from stock (20ul)
                        - Denature at 90C for 10mins''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0

    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    nuclease(protocol)
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
    tips201 = protocol.load_labware('opentrons_96_tiprack_20ul', 5)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
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

def incubate(start_time, minutes, protocol):
    end_time = start_time + minutes*60

    try:
        if not protocol.is_simulating():
            while time.time() < end_time:
                time.sleep(1)
        else:
            print('Not waiting, simulating')
    except KeyboardInterrupt:
        pass
        print()

def nuclease(protocol):
    enzy_col = start_96well
    buff_col = enzy_col+1
    samp_col = buff_col+1
    sdsb_col = samp_col+1

    tempdeck.set_temperature(celsius=37)

    #add buffer
    p300m.pick_up_tip()
    p300m.distribute(10, plate96.rows()[0][buff_col],
                     temp_pcr.rows()[0][1:7].bottom(1.5),
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()

    #titrate enzymes
    p20m.pick_up_tip()
    p20m.transfer(20, plate96.rows()[0][enzy_col],
                   temp_pcr.rows()[0][0].bottom(1.5), new_tip='never')
    p20m.transfer(10, temp_pcr.rows()[0][0:5].bottom(1.5),
                   temp_pcr.rows()[0][1:6].bottom(1.5),
                   mix_after=(3, 10), new_tip='never')
    p20m.aspirate(10, temp_pcr.rows()[0][5].bottom(1.5))
    p20m.drop_tip()

    #add nucleic acid
    p20m.transfer(10, plate96.rows()[0][samp_col],
                     temp_pcr.rows()[0][0:7].bottom(1.5),
                     disposal_volume=0, new_tip='always', 
                     mix_after=(3,10))
    
    #incubate 15mins at 37C
    start_time1=time.time()
    incubate(start_time1, 15, protocol)

    #add sds buff to samples
    p20m.transfer(20, plate96.rows()[0][sdsb_col],
                     temp_pcr.rows()[0][0:7].bottom(1.5),
                     disposal_volume=0, new_tip='always', 
                     mix_after=(3,10))

    #heat inactive at 90C for 10mins
    tempdeck.set_temperature(celsius=90)
    start_time2=time.time()
    incubate(start_time2, 10, protocol)
    tempdeck.deactivate()
