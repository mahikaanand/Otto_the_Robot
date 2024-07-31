from opentrons import protocol_api
import time


metadata = {
    'protocolName': '2D xtal screen in 48well plate',
    'author': 'Shawn Laursen',
    'description': '''Put:
                      - buff in trough 1
                      - water in trough 2
                      - X buff in trough 3
                      - Y buff in trough 4
                      - protein in A1 of 24well temp block''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="plate_side",
        display_name="Side of plate",
        description="Side of the 48 well plate on which to set up screen.",
        choices=[
            {"display_name": "Top", "value": 0},
            {"display_name": "Bottom", "value": 4},
        ],
        default=0,
    )
    parameters.add_float(
        variable_name="prot_drop",
        display_name="Protein drop size",
        description="Amount of protein solution to add to drop (can't exceed 10µL when combined with buff drop).",
        default=2.0,
        minimum=1.0,
        maximum=9.0,
        unit="µL"
    )
    parameters.add_float(
        variable_name="buff_drop",
        display_name="Buff drop size",
        description="Amount of buff solution to add to drop (can't exceed 10µL when combined with protein drop).",
        default=2.0,
        minimum=1.0,
        maximum=9.0,
        unit="µL"
    )
    parameters.add_int(
        variable_name="well_vol",
        display_name="Well volume",
        description="Amount of buff to make in each well (probably >50x of drop size).",
        default=300,
        minimum=50,
        maximum=300,
        unit="µL"
    )
    parameters.add_int(
        variable_name="temp",
        display_name="Temp deck temperature",
        default=4,
        minimum=4,
        maximum=100,
        unit="C"
    )
    parameters.add_float(
        variable_name="x_stock",
        display_name="X stock concentration",
        default=100.0,
        minimum=0.0,
        maximum=10000.0,
    )
    parameters.add_float(
        variable_name="x_high",
        display_name="HIGH X gradient concentration.",
        default=25.0,
        minimum=0.0,
        maximum=10000.0,
    )
    parameters.add_float(
        variable_name="x_low",
        display_name="LOW X gradient concentration.",
        default=0.0,
        minimum=0.0,
        maximum=10000.0,
    )
    parameters.add_float(
        variable_name="y_stock",
        display_name="Y stock concentration",
        default=1000.0,
        minimum=0.0,
        maximum=10000.0,
    )
    parameters.add_float(
        variable_name="y_high",
        display_name="HIGH Y gradient concentration.",
        default=250.0,
        minimum=0.0,
        maximum=10000.0,
    )
    parameters.add_float(
        variable_name="y_low",
        display_name="LOW Y gradient concentration.",
        default=0.0,
        minimum=0.0,
        maximum=10000.0,
    )
    parameters.add_float(
        variable_name="buff_stock",
        display_name="Buff stock concentration",
        default=1000.0,
        minimum=0.0,
        maximum=10000.0,
    )
    parameters.add_float(
        variable_name="buff_con",
        display_name="CONSTANT BUFFER concentration.",
        default=100.0,
        minimum=0.0,
        maximum=10000.0,
    )

def run(protocol):
    global plate_side, well_vol, x_stock, x_high, x_low, y_stock, y_high, y_low, buff_stock, buff_con
    plate_side = protocol.params.plate_side
    well_vol = protocol.params.well_vol
    x_stock = protocol.params.x_stock
    x_high = protocol.params.x_high
    x_low = protocol.params.x_low
    y_stock = protocol.params.y_stock
    y_high = protocol.params.y_high
    y_low = protocol.params.y_low
    buff_stock = protocol.params.buff_stock
    buff_con = protocol.params.buff_con

    strobe(12, 8, True, protocol)
    setup(protocol)
    tempdeck.set_temperature(celsius=protocol.params.temp)
    make_screen(protocol)
    add_protein(protocol.params.prot_drop, protocol)
    add_drop(protocol.params.buff_drop, protocol)
    tempdeck.deactivate()
    strobe(12, 8, False, protocol)

def setup(protocol):
    #equiptment
    global tips20, tips300, plate48, trough, p20m, p300m, tempdeck, temp_buffs
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    plate48 = protocol.load_labware('hampton_48_wellplate_combine', 5)
    trough = protocol.load_labware('nest_12_reservoir_15ml', 2)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=[tips20])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tips300])
    p20m.flow_rate.aspirate = 30
    p20m.flow_rate.dispense = 30
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_buffs = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')
    
    # buffs
    global buff, water, x_buff, y_buff, protein
    buff = trough.wells()[0]
    water = trough.wells()[1]
    x_buff = trough.wells()[2]
    y_buff = trough.wells()[3]
    protein = temp_buffs.wells()[0]

    # tips
    global tip20_dict, tip300_dict
    tip20_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}
    tip300_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}

    # colors 
    greenBuff = protocol.define_liquid(
        name="Buff",
        description="Buff",
        display_color="#00FF00",
    )
    buff.load_liquid(liquid=greenBuff, volume=5000)

    blueWater = protocol.define_liquid(
        name="Water",
        description="Water",
        display_color="#0000FF",
    )
    water.load_liquid(liquid=blueWater, volume=5000)

    redXBuff = protocol.define_liquid(
        name="X buff",
        description="X buff",
        display_color="#FF0000",
    )
    x_buff.load_liquid(liquid=redXBuff, volume=5000)

    colorYBuff = protocol.define_liquid(
        name="Y buff",
        description="Y buff",
        display_color="#FFFF00",
    )
    y_buff.load_liquid(liquid=colorYBuff, volume=5000)

    colorProtein = protocol.define_liquid(
        name="Protein",
        description="Protein",
        display_color="#00FFFF",
    )
    protein.load_liquid(liquid=colorProtein, volume=200)

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

def strobe(blinks, hz, leave_on, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)

def make_screen(protocol):
    # add buff to all wells of screen
    buff_vol = well_vol * (buff_con/buff_stock)
    x_step = (x_high-x_low) / 5
    y_step = (y_high-y_low) / 3
    pickup_tips(4, p300m, protocol)
    for col in range(1, 13, 2):
        p300m.aspirate(buff_vol, buff)
        p300m.dispense(buff_vol, plate48.rows()[plate_side][col])
    p300m.drop_tip()

    # add water to all wells 
    pickup_tips(1, p300m, protocol)
    for well in range(0, 24):
        col = well // 4
        row = well % 4
        x_vol = well_vol * ((col*x_step)/x_stock)
        y_vol = well_vol * ((row*y_step)/y_stock)
        water_vol = well_vol - (buff_vol+x_vol+y_vol)
        p300m.aspirate(water_vol, water)
        p300m.dispense(water_vol, plate48.rows()[row+plate_side][(col*2)+1])
    p300m.drop_tip()

    # add y buffs to wells
    for well in range(0, 24):
        col = well // 4
        row = well % 4
        y_vol = well_vol * ((row*y_step)/y_stock)
        if y_vol > 0:
            pickup_tips(1, p300m, protocol)
            p300m.aspirate(y_vol, y_buff)
            p300m.dispense(y_vol, plate48.rows()[row+plate_side][(col*2)+1])
            p300m.drop_tip()

    # add x buffs to wells
    for col in range(0, 6):
        x_vol = well_vol * ((col*x_step)/x_stock)
        pickup_tips(4, p300m, protocol)
        p300m.aspirate(x_vol, x_buff, rate=0.1)
        protocol.delay(seconds=10)
        p300m.move_to(x_buff.top(5))
        protocol.delay(seconds=10)
        p300m.dispense(x_vol, plate48.rows()[plate_side][(col*2)+1], rate=0.1)
        p300m.mix(8, well_vol/2)
        p300m.drop_tip()

def add_protein(prot_drop, protocol):
    # place rows worth of protein in first col
    pickup_tips(1, p300m, protocol)
    p300m.aspirate((prot_drop*24)+5, protein, rate=0.1)
    for row in range(0,4):
        p300m.dispense(prot_drop*6, plate48.rows()[row+plate_side][0].bottom(-1))
        p300m.touch_tip(radius=0.5, speed=15.0)
    p300m.drop_tip()

    # dispense drops from first col
    pickup_tips(4, p20m, protocol)
    p20m.aspirate(prot_drop*5, plate48.rows()[plate_side][0].bottom(-1), rate=0.1)
    for i in range(2,12,2):
        p20m.dispense(prot_drop, plate48.rows()[plate_side][i].bottom(-1), rate=0.1)
    p20m.drop_tip()

def add_drop(buff_drop, protocol):
    for i in range(0,12,2):
        pickup_tips(4, p20m, protocol)
        p20m.aspirate(buff_drop, plate48.rows()[plate_side][i+1])
        p20m.dispense(buff_drop, plate48.rows()[plate_side][i].bottom(-1))
        p20m.mix(5, buff_drop)
        p20m.drop_tip()
