from opentrons import protocol_api
import time


metadata = {
    'protocolName': 'Nuclease - prep samples for gel (part 2)',
    'author': 'Shawn Laursen',
    'description': '''You put mixes in 96 well plate: 
                        - 200ul SDS-urea buffer in col 3 (index from 0)
                        - 300ul of formamide in col 4 (index from 0)
                      Robot:
                        - Add SDS buff to all wells from stock (20ul)
                        - Add Formamide (40ul)
                        - Denature at 95C for 10mins''',
    'apiLevel': '2.11'
    }

def run(protocol):
    well_96start = 0 #index from 0

    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    prep(protocol)
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

def prep(protocol):
    enzy_col = start_96well
    buff_col = enzy_col+1
    samp_col = buff_col+1
    sdsb_col = samp_col+1
    form_col = sdsb_col+1

    #add sds buff to samples
    p20m.transfer(20, plate96.rows()[0][sdsb_col],
                     temp_pcr.rows()[0][0:7],
                     disposal_volume=0, new_tip='always', 
                     mix_after=(3,10))

    #add formamide buff to samples
    p300m.transfer(40, plate96.rows()[0][form_col],
                     temp_pcr.rows()[0][0:7],
                     disposal_volume=0, new_tip='always', 
                     mix_after=(3,20))

    #heat inactive at 95C for 10mins
    tempdeck.set_temperature(celsius=95)
    start_time2=time.time()
    incubate(start_time2, 10, protocol)
    tempdeck.deactivate()
