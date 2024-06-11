from opentrons import protocol_api
import time


metadata = {
    'protocolName': 'Nicole\'s nuclease assay',
    'author': 'Shawn Laursen',
    'description': '''You put mixes in 96 well plate:
                        - 30ul 2x enzyme in col 1
                        - 100ul buffer in col 2
                        - 100ul nucleic acid/protein in col 3 
                        - 30ul quench buffer in col 
                      Robot:
                        - Heat block to 20C 
                        - Titrate 2x enzymes in pcr tubes 1:1 6 times, leaving #7 as control (10ul) 
                        - Add 2x nucleic acid/protein stock (10ul) 
                        - Incubate at 20C for 20mins 
                        - Add quench buff to all wells from stock (2ul) 
                        - Incubate at 37C for 10mins''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="well_96start",
        display_name="96 column start",
        description="Which column to start in. Indexed from 1.",
        default=1,
        minimum=1,
        maximum=12,
        unit="column"
    )
    parameters.add_int(
        variable_name="incubation_temp",
        display_name="Incubation temp",
        description="Incubation temp of reaction.",
        default=20,
        minimum=4,
        maximum=95,
        unit="C"
    )
    parameters.add_int(
        variable_name="incubation_time",
        display_name="Incubation time",
        description="Incubation duration.",
        default=20,
        minimum=0,
        maximum=1000,
        unit="min"
    )
    parameters.add_int(
        variable_name="quench_temp",
        display_name="Quenching temp",
        description="Queching temp of proteinase K.",
        default=37,
        minimum=4,
        maximum=95,
        unit="C"
    )
    parameters.add_int(
        variable_name="quench_time",
        display_name="Quenching time",
        description="Queching duration of proteinase K.",
        default=10,
        minimum=0,
        maximum=1000,
        unit="min"
    )

def run(protocol):
    well_96start = protocol.params.well_96start - 1
    incubation_temp = protocol.params.incubation_temp
    quench_temp = protocol.params.quench_temp
    incubation_time = protocol.params.incubation_time
    quench_time = protocol.params.quench_time
    strobe(12, 8, True, protocol)
    setup(well_96start, protocol)
    nuclease(protocol, incubation_temp, quench_temp, incubation_time, quench_time)
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

def nuclease(protocol, incubation_temp, quench_temp, incubation_time, quench_time):
    enzy_col = start_96well
    buff_col = enzy_col+1
    samp_col = buff_col+1
    sdsb_col = samp_col+1
    form_col = sdsb_col+1

    tempdeck.set_temperature(celsius=incubation_temp)

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
    start_time1=time.time()
    p20m.transfer(10, plate96.rows()[0][samp_col],
                     temp_pcr.rows()[0][0:7],
                     disposal_volume=0, new_tip='always', 
                     mix_after=(3,10))
    
    #incubate
    incubate(start_time1, incubation_time, protocol)

    #add quench buff to samples
    p20m.transfer(2, plate96.rows()[0][sdsb_col],
                     temp_pcr.rows()[0][0:7],
                     disposal_volume=0, new_tip='always', 
                     mix_after=(3,10))

    #quench
    tempdeck.set_temperature(celsius=quench_temp)
    start_time2=time.time()
    incubate(start_time2, quench_time, protocol)
    tempdeck.deactivate()
