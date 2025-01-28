from opentrons import protocol_api
import time

metadata = {
    'protocolName': '5cmpd PARPi HPLC Assay pt.3',
    'author': 'Thomas Stilley',
    'description': '''HPLC pt.3
                    Tips: 
                    1 p300 tip per sample
                    
                    - Pull off 90uL supernatant and transfer into HPLC insert''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
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
        variable_name="RXN_time",
        display_name="P1 RXN time",
        description="Reaction duration for PARP1 reaction.",
        default=2,
        minimum=0,
        maximum=1000,
        unit="min"
    )

def run(protocol):
    # set variables
    start_96well = protocol.params.start_96well - 1
    RXN_time = protocol.params.RXN_time
   

    # run protocol
    strobe(12, 8, True, protocol)
    setup(protocol)
    HPLC(RXN_time, protocol)
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
    global tips300, p300m, plate96, Block1
    
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 5)
    Block1 = protocol.load_labware('custom_24_aluminumblock_250uL', 4)

    # tips
    global tip20_dict, tip300_dict
    tip20_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}
    tip300_dict = {key: ['H','G','F','E','D','C','B','A'] for key in range(1, 12 + 1)}

def pickup_tips(number, pipette, protocol):

    if pipette == p300m:
        for col in tip300_dict:
            if len(tip300_dict[col]) >= number:
                p300m.pick_up_tip(tips300[str(tip300_dict[col][number-1] + str(col))])
                tip300_dict[col] = tip300_dict[col][number:]
                break

def HPLC(RXN_time, protocol):
     
     # Remove Supernatant
    p300m.flow_rate.aspirate = 45
    p300m.well_bottom_clearance.aspirate = 3.5
    p300m.flow_rate.dispense = 45
    p300m.well_bottom_clearance.dispense = -1.5
        
    for i in range(0,24):
        pickup_tips(1, p300m, protocol)
        p300m.aspirate(55, plate96.wells()[i])
        p300m.dispense(55, Block1.wells()[i])
        p300m.drop_tip()

    protocol.delay(minutes=RXN_time)

    for i in range(24,48):
        pickup_tips(1, p300m, protocol)
        p300m.aspirate(55, plate96.wells()[i])
        p300m.dispense(55, Block1.wells()[i-24])
        p300m.drop_tip()

    protocol.delay(minutes=RXN_time)

    for i in range(48,72):
        pickup_tips(1, p300m, protocol)
        p300m.aspirate(55, plate96.wells()[i])
        p300m.dispense(55, Block1.wells()[i-48])
        p300m.drop_tip()

    protocol.delay(minutes=RXN_time)

    for i in range(72,96):
        pickup_tips(1, p300m, protocol)
        p300m.aspirate(55, plate96.wells()[i])
        p300m.dispense(55, Block1.wells()[i-72])
        p300m.drop_tip()


     

    



     

     

   


   

   

    

