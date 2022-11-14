from opentrons import protocol_api

metadata = {
    'protocolName': 'HTS_compound_dilution',
    'author': 'Johannes',
    'source': 'Protocol Library',
    'apiLevel': '2.5'
    }

def run(protocol_context):
    protocol_context.set_rail_lights(True)

    # labware
    compound_plates = [protocol_context.load_labware("costar_96_wellplate_200ul", x) for x in range(1, 7)]
    trough = protocol_context.load_labware("nest_12_reservoir_15ml", '8')
    dmso_troughs = [trough.wells()[x] for x in range (0, 6)]
    liquid_trash = trough.wells()[-1]
    tiprack = [protocol_context.load_labware('opentrons_96_tiprack_300ul', '7')]
    pipette = protocol_context.load_instrument("p300_multi_gen2", mount='left', tip_racks=tiprack)

    compound_dilution = CompoundDilution(protocol_context, pipette, liquid_trash)

    # Distribute DMSO across the plate to the the number of samples
    for i in range(0, 6):
        pipette.pick_up_tip()
        compound_dilution.fill_plate_with_dmso(dmso=dmso_troughs[i], compound_plate=compound_plates[i], rangestart=1, rangeend=12)
        compound_dilution.serial_dilution(compound_plate=compound_plates[i], rangestart=0, num_of_dilutions=11)
        pipette.drop_tip()

    # turn off robot rail lights
    protocol_context.set_rail_lights(False)

class CompoundDilution:
    def __init__(self, ctx, pipette, liquid_trash):
        self.ctx = ctx
        self.pipette = pipette
        self.liquid_trash = liquid_trash

    def fill_plate_with_dmso(self, dmso, compound_plate, rangestart, rangeend):
        for row in range(rangestart, rangeend):
            self.pipette.transfer(
                100,
                dmso,
                compound_plate.rows()[0][row],
                new_tip="never"
             )   

    def serial_dilution(self, compound_plate, rangestart, num_of_dilutions):
        for i in range(rangestart, num_of_dilutions): 
            self.pipette.transfer(
                100,
                compound_plate.rows()[0][i],
                compound_plate.rows()[0][i+1],
                mix_after=(5, 100),
                new_tip="never"
            )
