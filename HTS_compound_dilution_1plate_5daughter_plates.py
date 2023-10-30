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
    compound_plate = protocol_context.load_labware("costar_96_wellplate_200ul",1)
    daughter_plates = [protocol_context.load_labware("costar_96_wellplate_200ul",x) for x in [2, 3, 4, 5, 6]]
    trough = protocol_context.load_labware("nest_12_reservoir_15ml", '8')
    dmso_troughs = trough.wells()[0]
    tiprack = [protocol_context.load_labware('opentrons_96_tiprack_300ul', '7')]
    pipette = protocol_context.load_instrument("p300_multi_gen2", mount='left', tip_racks=tiprack)

    compound_dilution = CompoundDilution(protocol_context, pipette)

    # Distribute DMSO across the plate to the the number of samples
    pipette.pick_up_tip()
    compound_dilution.fill_plate_with_dmso(dmso=dmso_troughs, compound_plate=compound_plate, rangestart=1, rangeend=12)
    # Serial dilution down the plate
    compound_dilution.serial_dilution(compound_plate=compound_plate, rangestart=0, num_of_dilutions=11)
    pipette.drop_tip()
    # Make 5 daughter plates
    pipette.pick_up_tip()
    compound_dilution.make_daughters(compound_plate=compound_plate, daughter_plates=daughter_plates, rangestart=0, rangeend=12)
    pipette.drop_tip()

    # turn off robot rail lights
    protocol_context.set_rail_lights(False)

class CompoundDilution:
    def __init__(self, ctx, pipette):
        self.ctx = ctx
        self.pipette = pipette

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

    def make_daughters(self, compound_plate, daughter_plates, rangestart, rangeend):
        for row in range(rangestart, rangeend):
            self.pipette.distribute(
                        15,
                        compound_plate.rows()[0][row],
                        [plate.rows()[0][row] for plate in daughter_plates],
                        disposal_volume=10,
                        new_tip="never"
            )