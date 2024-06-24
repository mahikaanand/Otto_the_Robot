from opentrons import protocol_api
import time, math

metadata = {
    'protocolName': 'MNase digest assay',
    'author': 'Sashi Weerawarana',
    'description': '''You put mixes in 96 well plate:
                        - 30 ul 2x enzyme in col 1
                        - 100 ul buffer in col 2
                        - 40 ul nucleic acid/protein in col 3 
                        - 100 ul edta in col 4
                        - 10 ul prok in col 5
                      Robot:
                        - Heat block to incubation_temp 
                        - Titrate 2x enzymes in pcr tubes 1:1 4 times, leaving #5 as control (10ul) 
                        - Add 30 ul complex to each pcr tube 
                        - Incubate at incubation_temp for incubation_time 
                        - Add edta to all wells from stock (10 ul)
                        - Add proK to all wells from stock (1 ul)
                        - Incubate at prok_temp for prok_time''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="num_samples",
        display_name="number of samples",
        description="How many samples you have.",
        default=1,
        minimum=1,
        maximum=8,
        unit="samples"
    )

    parameters.add_int(
        variable_name="start_96well",
        display_name="96 column start",
        description="Which column to start in. Indexed from 1.",
        default=1,
        minimum=1,
        maximum=12,
        unit="column"
    )
    parameters.add_int(
        variable_name="mnase_temp",
        display_name="MNase incubation temp",
        description="Incubation temp of MNase reaction.",
        default=37,
        minimum=4,
        maximum=95,
        unit="C"
    )
    parameters.add_int(
        variable_name="mnase_time",
        display_name="MNase incubation time",
        description="Incubation duration for MNase reaction.",
        default=10,
        minimum=0,
        maximum=1000,
        unit="min"
    )
    parameters.add_int(
        variable_name="prok_temp",
        display_name="ProK incubation temp",
        description="Incubation temp of proteinase K.",
        default=50,
        minimum=4,
        maximum=95,
        unit="C"
    )
    parameters.add_int(
        variable_name="prok_time",
        display_name="ProK incubation time",
        description="Incubation duration of proteinase K.",
        default=30,
        minimum=0,
        maximum=1000,
        unit="min"
    )

def run(protocol):
    # set variables
    num_samples = protocol.params.num_samples
    start_96well = protocol.params.start_96well - 1
    mnase_temp = protocol.params.mnase_temp
    mnase_time = protocol.params.mnase_time
    prok_temp = protocol.params.prok_temp
    prok_time = protocol.params.prok_time

    # run protocol
    strobe(12, 8, True, protocol)
    setup(protocol)
    mnase(num_samples, start_96well, mnase_temp, mnase_time, protocol)
    prok(prok_temp, prok_time, protocol)
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

def setup(protocol):
    # equipment
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

    #single tips
    global which_tips20, tip20
    which_tips20 = []
    tip20 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips20.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

    #single tips
    global which_tips300, tip300
    which_tips300 = []
    tip300 = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips300.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

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

def pickup_tips(number, pipette, protocol):
    global tip300, tip20

    if pipette == p20m:
        if (tip20 % number) != 0:
            while (tip20 % 8) != 0:
                tip20 += 1
        tip20 += number-1
        p20m.pick_up_tip(tips20[which_tips20[tip20]])
        tip20 += 1 
    if pipette == p300m:
        if (tip300 % number) != 0:
            while (tip300 % 8) != 0:
                tip300 += 1
        tip300 += number-1
        p300m.pick_up_tip(tips300[which_tips300[tip300]])
        tip300 += 1

def mnase(num_samples, start_96well, mnase_temp, mnase_time, protocol):
    # set variables
    global edta_col

    enz_col = start_96well
    buff_col = enz_col+1
    samp_col = buff_col+1
    edta_col = samp_col+1

    # set temp deck
    tempdeck.set_temperature(celsius=mnase_temp)

    # add buffer
    pickup_tips(num_samples, p300m, protocol)
    p300m.distribute(10, plate96.rows()[0][buff_col],
                     temp_pcr.rows()[0][1:4],
                     disposal_volume=10, new_tip='never')
    p300m.drop_tip()

    # titrate enzymes
    pickup_tips(num_samples, p20m, protocol)
    p20m.transfer(20, plate96.rows()[0][enz_col], 
                  temp_pcr.rows()[0][0], new_tip='never')
    p20m.transfer(10, temp_pcr.rows()[0][0:2], 
                  temp_pcr.rows()[0][1:3], 
                  mix_after=(3, 10), new_tip='never')
    p20m.aspirate(10, temp_pcr.rows()[0][5])
    p20m.drop_tip()

    # add complex
    p300m.transfer(30, plate96.rows()[0][samp_col], 
                  temp_pcr.rows()[0][0:4], 
                  disposal_volume=0, new_tip='always', 
                  mix_after=(3,10))
    
    start_time1=time.time()

    # incubate
    incubate(start_time1, mnase_time, protocol)

    # quench
    p20m.transfer(10, plate96.rows()[0][edta_col], 
                  temp_pcr.rows()[0][0:4], 
                  disposal_volume=0, new_tip='always', 
                  mix_after=(3,10))

def prok(prok_temp, prok_time, protocol):
    prok_col = edta_col+1

    # add proK
    p20m.transfer(1, plate96.rows()[0][prok_col], 
                  temp_pcr.rows()[0][0:4], 
                  disposal_volume=0, new_tip='always', 
                  mix_after=(3,10))

    # set temp deck
    tempdeck.set_temperature(celsius=prok_temp)

    # incubate
    start_time2=time.time()
    incubate(start_time2, prok_time, protocol)
    tempdeck.deactivate()
