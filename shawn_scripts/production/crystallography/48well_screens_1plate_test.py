from opentrons import protocol_api
import time


metadata = {
    'protocolName': 'Crystallography - 2 x 48well Crystal Tray Setup',
    'author': 'Shawn Laursen',
    'description': '''Takes 96well block and sets up 2x48well trays
                      with protein drops. Need a little overage of 
                      protein. 
                      >300ul of each 96well condition in block.
                      6xprot_drop + ~5ul of protein in each tube 
                      of strip tube.''',
    'apiLevel': '2.11'
    }

def run(protocol):
    global prot_drop, buff_drop
    prot_drop = 2
    buff_drop = 2
    strobe(12, 8, True, protocol)
    setup(4, protocol)
    # tempdeck.set_temperature(celsius=4)
    for plate in plates:
        add_screen(plate, protocol)
        add_drop(plate, protocol)
        test(protocol)
        # add_protein(plate, protocol)
    # tempdeck.deactivate()
    strobe(12, 8, False, protocol)


def setup(num_buffs, protocol):
    #equiptment
    global tips20, tips300, plate48, plate48_2, screen_block, p20m, p300m, tempdeck, temp_pcr
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    plate48 = protocol.load_labware('hampton_48_wellplate_combine', 1)
    screen_block = protocol.load_labware('thermoscientificnunc_96_wellplate_2000ul', 2)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    p20m.flow_rate.aspirate = 30
    p20m.flow_rate.dispense = 30
    tempdeck = protocol.load_module('temperature module gen2', 10)
    temp_pcr = tempdeck.load_labware(
                 'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    
    global plates
    plates = [plate48]

def strobe(blinks, hz, leave_on, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)

def add_screen(plate, protocol):
    if plate == plate48:
        buffx = 0
    elif plate == plate48_2:
        buffx = 6

    p300m.transfer(200+buff_drop, 
                   screen_block.rows()[0][buffx:buffx+6],
                   plate.rows()[0][1:13:2], 
                   mix_before=(5,300),
                   new_tip='always')

def add_drop(plate, protocol):
    for i in range(0,12,2):
        p20m.pick_up_tip()
        p20m.aspirate(buff_drop, plate.rows()[0][i+1])
        p20m.dispense(buff_drop, plate.rows()[0][i].top(-1.8))
        p20m.drop_tip()

def add_protein(plate, protocol):
    for i in range(0,4,2):
        p20m.pick_up_tip()
        p20m.aspirate(prot_drop, temp_pcr.rows()[0][0].bottom(0))
        p20m.dispense(prot_drop, plate.rows()[0][i].top(-1.8))
        p20m.mix(repetitions=3, volume=prot_drop)
        p20m.drop_tip()
    for i in range(4,8,2):
        p20m.pick_up_tip()
        p20m.aspirate(prot_drop, temp_pcr.rows()[0][0].bottom(0))
        p20m.dispense(prot_drop, plate.rows()[0][i].top(-1.8))
        p20m.drop_tip()
    for i in range(8,12,2):
        p20m.pick_up_tip()
        p20m.aspirate(prot_drop, temp_pcr.rows()[0][0].bottom(0))
        p20m.move_to(plate.rows()[0][i].top(-1.8))
        p20m.dispense(prot_drop, plate.rows()[0][i])
        p20m.mix(repetitions=3, volume=prot_drop)
        p20m.drop_tip()

def test(protocol):
    height = 0
    p20m.pick_up_tip()
    for i in range(0,12,2):
        p20m.move_to(plate.rows()[0][i].top(-1.8))
        p20m.dispense(prot_drop, plate.rows()[0][i].bottom(height))
        protocol.delay(seconds=5)
        height += 1
    p20m.drop_tip()

