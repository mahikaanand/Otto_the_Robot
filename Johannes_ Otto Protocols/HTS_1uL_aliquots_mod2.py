from opentrons import protocol_api
from opentrons.types import Point

def get_values(*names):
    import json
    _all_values = json.loads("""{"pipette_type":"p20_multi_gen2","tip_type":0,"trough_type":"nest_12_reservoir_15ml","plate_type":"corning3575_384well_alt","dilution_factor":2,"num_of_dilutions":11,"total_mixing_volume":20,"tip_use_strategy":"never"}""")
    return [_all_values[n] for n in names]


metadata = {
    'protocolName': 'High Throuput Screen for PARP ± HPF1',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.5'
    }

def run(protocol_context):
    [pipette_type, tip_type, trough_type,
     dilution_factor, num_of_dilutions, total_mixing_volume,
        tip_use_strategy] = get_values(  # noqa: F821
            'pipette_type', 'tip_type', 'trough_type',
            'dilution_factor', 'num_of_dilutions',
            'total_mixing_volume', 'tip_use_strategy'
        )

    # assert that the world is the way we want it to be
    assert 'multi' in pipette_type, "wrong pipette_type"

    # turn on robot rail lights
    protocol_context.set_rail_lights(True)

    # labware
    compound_plate_1 = protocol_context.load_labware("costar_96_wellplate_200ul", '1')
    compound_plate_2 = protocol_context.load_labware("costar_96_wellplate_200ul", '2')
    assay_plate = protocol_context.load_labware("corning3575_384well_alt", '3')
    trough = protocol_context.load_labware(trough_type, '6')
    buffer = trough.wells()[0]
    enzyme_1 = trough.wells()[1]
    enzyme_2 = trough.wells()[2]
    liquid_trash = trough.wells()[-1]
    tip_name = 'opentrons_96_tiprack_20ul'

    tiprack = [
        protocol_context.load_labware(tip_name, slot)
        for slot in ['11']
    ]

    pipette = protocol_context.load_instrument(
        pipette_type, mount='right', tip_racks=tiprack)

    pipette.flow_rate.aspirate = 10
    pipette.flow_rate.dispense = 10

    transfer_volume_compound = 1
    diluent_volume = 40

    assay_prep = AssayPrep(protocol_context, compound_plate_1, compound_plate_2, assay_plate, pipette, buffer, enzyme_1, enzyme_2, liquid_trash, transfer_volume_compound)

    #pipette.pick_up_tip()

    # Distribute buffer across the assay_plate to the the number of samples
    #loop to fill odd and even rows of assay_plate
    #assay_prep.fill_plate_with_buffer(evenodd=0, rangestart=0, rangeend=24)
    #assay_prep.fill_plate_with_buffer(evenodd=1, rangestart=0, rangeend=24)

    #pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+1) in 96-well compound_plate to (row+1, odd) in 384-well assay_plate
    for i in range(0,12):
        assay_prep.add_compound_1_to_assay(transfer_volume_compound=1, compound_row=i, compound_plate_1=compound_plate_1, assay_row=i, evenodd=0)
        assay_prep.add_compound_1_to_assay(transfer_volume_compound=1, compound_row=i, compound_plate_1=compound_plate_1, assay_row=i+12, evenodd=0)

    pipette.drop_tip()
    pipette.pick_up_tip()

    for i in range(0,12):
        assay_prep.add_compound_2_to_assay(transfer_volume_compound=1, compound_row=i, compound_plate_2=compound_plate_2, assay_row=i, evenodd=1)
        assay_prep.add_compound_2_to_assay(transfer_volume_compound=1, compound_row=i, compound_plate_2=compound_plate_2, assay_row=i+12, evenodd=1)

    pipette.drop_tip()

    # Distribute enzyme mixes across the assay_plate to the the number of samples
    pipette.pick_up_tip()
    #loop to fill odd and even rows of assay_plate
    assay_prep.fill_plate_with_enzyme_1(evenodd=0, rangestart=0, rangeend=12)
    assay_prep.fill_plate_with_enzyme_1(evenodd=1, rangestart=0, rangeend=12)

    #loop to fill odd and even rows of assay_plate
    assay_prep.fill_plate_with_enzyme_2(evenodd=0, rangestart=12, rangeend=24)
    assay_prep.fill_plate_with_enzyme_2(evenodd=1, rangestart=12, rangeend=24)


    pipette.drop_tip()

    # turn off robot rail lights
    protocol_context.set_rail_lights(False)  

class AssayPrep:
    def __init__(self, ctx, compound_plate_1, compound_plate_2, assay_plate, pipette, buffer, enzyme_1, enzyme_2, liquid_trash, transfer_volume_compound):
        self.ctx = ctx
        self.compound_plate_1 = compound_plate_1
        self.compound_plate_2 = compound_plate_2
        self.assay_plate = assay_plate
        self.pipette = pipette
        self.buffer = buffer 
        self.pipette.blow_out = pipette.blow_out
        self.enzyme_1 = enzyme_1
        self.enzyme_2 = enzyme_2
        self.liquid_trash = liquid_trash
        self.transfer_volume_compound = transfer_volume_compound      


    def fill_plate_with_buffer(self, evenodd, rangestart, rangeend):
        for row in range(rangestart, rangeend):
            self.pipette.transfer(
                20,
                self.buffer,
                self.assay_plate.rows()[evenodd][row],
                new_tip="never"
            )       

    def add_compound_1_to_assay(self, transfer_volume_compound, compound_plate_1, compound_row, assay_row, evenodd):     
        self.pipette.transfer(
                transfer_volume_compound,
                self.compound_plate_1.rows()[0][compound_row],
                self.assay_plate.rows()[evenodd][assay_row],
                self.pipette.blow_out(),
                new_tip="never"
        )    

    def add_compound_2_to_assay(self, transfer_volume_compound, compound_plate_2, compound_row, assay_row, evenodd):     
        self.pipette.transfer(
                transfer_volume_compound,
                self.compound_plate_2.rows()[0][compound_row],
                self.assay_plate.rows()[evenodd][assay_row],
                self.pipette.blow_out(),
                new_tip="never"
        )        


    def fill_plate_with_enzyme_1 (self, evenodd, rangestart, rangeend):

        for row in range(rangestart, rangeend):

            self.pipette.transfer(
                10,
                self.enzyme_1,
                self.assay_plate.rows()[evenodd][row],
                new_tip="never"
            )

    def fill_plate_with_enzyme_2 (self, evenodd, rangestart, rangeend):

        for row in range(rangestart, rangeend):

            self.pipette.transfer(
                10,
                self.enzyme_2,
                self.assay_plate.rows()[evenodd][row],
                new_tip="never"

            )
  
