from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Crosslinker titration',
    'author': 'Shawn Laursen',
    'description': '''This protocol will do a crosslinking reaction at 3 concentrations of BS3. It's going 
                      to use the first 3 wells to distribute crosslinker, so don't use those. Starting column
                      should be the first of these empty columns, you'll put protein in the fourth.
                      Liquids:
                      - Put 30µL of sample into pcr tray (every third column, starting in fourth column)
                      - Fill up 1ml tube of buff in first position of 24well
                      - Fill up >(10µL * num samples) 1ml tube of 2x BS3 in second position of 24well
                      - Fill up >(10µL * num samples) tube of 2000x BS3 in third position of 24well
                      - Fill up >(20µL * 3 * num samples) tube of glycine first position of trough
                      - Fill up >(40µL * 3 * num samples) tube of SDS second position of trough
                      ''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="num_samples",
        display_name="Number of samples",
        description="Number of samples.",
        default=8,
        minimum=1,
        maximum=24,
        unit="samples"
    )
    parameters.add_int(
        variable_name="temp_96start",
        display_name="Temp 96 well start",
        description="Which column to start in. Indexed from 1.",
        default=1,
        minimum=1,
        maximum=7,
        unit="column"
    )
    parameters.add_int(
        variable_name="incubation_temp",
        display_name="Incubation temp",
        description="Incubation temp of reaction.",
        default=37,
        minimum=4,
        maximum=95,
        unit="C"
    )
    parameters.add_int(
        variable_name="incubation_time",
        display_name="Incubation time",
        description="Incubation duration.",
        default=30,
        minimum=0,
        maximum=1000,
        unit="min"
    )
    parameters.add_int(
        variable_name="denature_temp",
        display_name="Denaturing temp",
        description="Temp to denature after quenching.",
        default=95,
        minimum=4,
        maximum=95,
        unit="C"
    )
    parameters.add_int(
        variable_name="denature_time",
        display_name="Denaturing time",
        description="Amount of time to denature after quench.",
        default=5,
        minimum=0,
        maximum=1000,
        unit="min"
    )

def run(protocol):
    global num_samples, temp_96start, num_cols, remainder
    num_samples = protocol.params.num_samples
    num_cols = num_samples // 8
    remainder = num_samples % 8
    temp_96start = protocol.params.temp_96start - 1
    incubation_temp = protocol.params.incubation_temp
    incubation_time = protocol.params.incubation_time
    denature_temp = protocol.params.denature_temp
    denature_time = protocol.params.denature_time

    strobe(12, 8, True, protocol)
    setup(protocol)
    
    distribute_samples(protocol)
    add_crosslinker(incubation_temp, protocol)
    incubate(incubation_time, protocol)
    quench(protocol)
    add_sample_buff(protocol)
    denature(denature_temp, denature_time, protocol)
    
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
    # equiptment
    global tips300, tips20, trough, p300m, p20m, tempdeck, temp_pcr, rt_24, glycine, sds
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    trough = protocol.load_labware('nest_12_reservoir_15ml', 2)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tips300])
    p20m = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=[tips20])
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware('opentrons_96_aluminumblock_nest_wellplate_100ul')
    rt_24 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 8)
    glycine = trough.wells()[0]
    sds = trough.wells()[1]

    # liquids
    grayReserved = protocol.define_liquid(
        name="Reserved",
        description="Reserved for robot",
        display_color="#000000",
    )
    for i in range(0, 3):
        for j in range(0, 8):
            temp_pcr.rows()[j][i].load_liquid(liquid=grayReserved, volume=50)

    yellowSamples = protocol.define_liquid(
        name="Samples",
        description="Samples",
        display_color="#FFFF00",
    )
    for i in range(0, (24 // 8)):
        col = (i*3) + 3
        for j in range(0, 8):
            temp_pcr.rows()[j][col].load_liquid(liquid=yellowSamples, volume=50)

    greenGlycine = protocol.define_liquid(
        name="Glycine",
        description="Glycine",
        display_color="#00FF00",
    )
    glycine.load_liquid(liquid=greenGlycine, volume=5000)

    grayBuff = protocol.define_liquid(
        name="Buff",
        description="Buff used for no BS3 control",
        display_color="#AAAAAA",
    )
    rt_24.rows()[0][0].load_liquid(liquid=grayBuff, volume=1600)

    redXL = protocol.define_liquid(
        name="2x BS3",
        description="2x BS3 that will be 1x final when added",
        display_color="#AA0000",
    )
    rt_24.rows()[0][1].load_liquid(liquid=redXL, volume=1600)

    redishXL = protocol.define_liquid(
        name="2000x BS3",
        description="2000x BS3 that will be 1000x final when added",
        display_color="#FF0000",
    )
    rt_24.rows()[0][2].load_liquid(liquid=redishXL, volume=1600)

    blueSDS = protocol.define_liquid(
        name="SDS buff",
        description="SDS buff",
        display_color="#0000FF",
    )
    sds.load_liquid(liquid=blueSDS, volume=5000)

    # tips
    global tip20_dict, tip300_dict
    tip20_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}
    tip300_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}

def pickup_tips(number, pipette, protocol):
    if pipette == p20m:
        for col in tip20_dict:
            if len(tip20_dict[col]) >= number:
                p20m.pick_up_tip(tips20[str(tip20_dict[col][number-1] + str(col))])
                tip20_dict[col] = tip20_dict[col][number:]
                break
    if pipette == p300m:
        for col in tip300_dict:
            if len(tip300_dict[col]) >= number:
                p300m.pick_up_tip(tips300[str(tip300_dict[col][number-1] + str(col))])
                tip300_dict[col] = tip300_dict[col][number:]
                break

def distribute_samples(protocol):
    # full 8 cols
    for i in range(0, (num_samples // 8)):
        col = (i*3) + temp_96start +3
        pickup_tips(8, p20m, protocol)
        p20m.distribute(10, temp_pcr.rows()[0][col], 
                      temp_pcr.rows()[0][col+1:col+3],
                      disposal_volume=0, new_tip='never')
        p20m.drop_tip()

    # remainder rows in last col
    if remainder != 0:
        try:
            col += 3
        except:
            col = temp_96start +3
        pickup_tips(remainder, p20m, protocol)
        p20m.distribute(10, temp_pcr.rows()[0][col], 
                        temp_pcr.rows()[0][col+1:col+3],
                        disposal_volume=0, new_tip='never')
        p20m.drop_tip()

def add_crosslinker(incubation_temp, protocol):    
    # disperse xl into 8 wells
    col = temp_96start
    for j in range(0,3):
        pickup_tips(1, p300m, protocol)
        p300m.aspirate((num_samples*10)+40, rt_24.rows()[0][j]) 
        for row in range(0, remainder):
            p300m.dispense(((num_cols+1)*10)+5, temp_pcr.rows()[row][col+j])
        for row in range(remainder, 8):  
            p300m.dispense(((num_cols)*10)+5, temp_pcr.rows()[row][col+j])  
        p300m.drop_tip()

    tempdeck.set_temperature(celsius=incubation_temp)
    global start_time
    start_time = time.time()

    # distribute
    for i in range(0, num_cols):
        col = (i*3) + temp_96start + 3
        for j in range(0,3):
            pickup_tips(8, p20m, protocol)
            p20m.aspirate(10, temp_pcr.rows()[0][temp_96start+j])
            p20m.dispense(10, temp_pcr.rows()[0][col+j])
            p20m.mix(3,10)
            p20m.drop_tip()

    if remainder != 0:
        try:
            col += 3
        except:
            col = temp_96start + 3
        for j in range(0,3):
            pickup_tips(remainder, p20m, protocol)
            p20m.aspirate(10, temp_pcr.rows()[0][temp_96start+j])
            p20m.dispense(10, temp_pcr.rows()[0][col+j])
            p20m.mix(3,10)
            p20m.drop_tip()

def incubate(incubation_time, protocol):
    end_time = start_time + incubation_time*60
    try:
        if not protocol.is_simulating():
            while time.time() < end_time:
                time.sleep(1)
        else:
            print('Not waiting, simulating')
    except KeyboardInterrupt:
        pass
        print()

def quench(protocol):
    # full 8 cols
    for i in range(0, num_cols):
        col = (i*3) + temp_96start + 3
        for j in range(0,3): 
            pickup_tips(8, p20m, protocol)
            p20m.aspirate(10,glycine) 
            p20m.dispense(10,temp_pcr.rows()[0][col+j])
            p20m.mix(3,20)  
            p20m.drop_tip()

    # remainder rows in last col
    if remainder != 0:
        try:
            col += 3
        except:
            col = temp_96start +3
        for j in range(0,3): 
            pickup_tips(remainder, p20m, protocol)
            p20m.aspirate(10,glycine) 
            p20m.dispense(10,temp_pcr.rows()[0][col+j])
            p20m.mix(3,20)  
            p20m.drop_tip()

def add_sample_buff(protocol):   
    # full 8 cols
    num_cols = num_samples // 8
    for i in range(0, num_cols):
        col = (i*3) + temp_96start + 3
        for j in range(0,3): 
            pickup_tips(8, p300m, protocol)
            p300m.aspirate(40,sds) 
            p300m.dispense(40,temp_pcr.rows()[0][col+j])
            p300m.mix(3,40)  
            p300m.drop_tip()

    # remainder rows in last col
    if remainder != 0:
        try:
            col += 3
        except:
            col = temp_96start +3
        for j in range(0,3): 
            pickup_tips(remainder, p300m, protocol)
            p300m.aspirate(40,sds) 
            p300m.dispense(40,temp_pcr.rows()[0][col+j])
            p300m.mix(3,40)  
            p300m.drop_tip()

def denature(denature_temp, denature_time, protocol):
    tempdeck.set_temperature(celsius=denature_temp)
    protocol.delay(minutes=denature_time)
    tempdeck.deactivate()
