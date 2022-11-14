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
    compound_plate = protocol_context.load_labware("costar_96_wellplate_200ul", '1')
    assay_plate = protocol_context.load_labware("corning3575_384well_alt", '3')
    trough = protocol_context.load_labware(trough_type, '2')
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

    pipette.flow_rate.aspirate = 7.5
    pipette.flow_rate.dispense = 15

    transfer_volume_compound = 1
    transfer_volume_dilution = 20
    diluent_volume = 40

    assay_prep = AssayPrep(protocol_context, compound_plate, assay_plate, pipette, buffer, enzyme_1, enzyme_2, liquid_trash, transfer_volume_compound, transfer_volume_dilution)

    # Distribute buffer across the assay_plate to the the number of samples
    # And add diluent to one column after the number of samples for a blank
    pipette.pick_up_tip()
    #loop to fill odd and even rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=0, rangestart=0, rangeend=24)
    assay_prep.fill_plate_with_buffer(evenodd=1, rangestart=0, rangeend=24)

    #add extra buffer to first columns of dilution in assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=0, rangestart=0, rangeend=1)
    #ladd extra buffer to right odd rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=0, rangestart=12, rangeend=13)
    #add extra buffer to even rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=1, rangestart=0, rangeend=1)
    #add extra buffer to right even rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=1, rangestart=12, rangeend=13)

    pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+1) in 96-well compound_plate to (row+1, odd) in 384-well assay_plate; then do 11 serial dilutions
    assay_prep.add_compound_to_assay(transfer_volume_compound=1, mixing_volume=20, compound_row=0, assay_row=0, evenodd=0)
    assay_prep.serial_dilution(evenodd=0, rangestart=1, num_of_dilutions=num_of_dilutions)

    pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+1) in 96-well compound_plate to (row12+1, odd) in 384-well assay_plate; then do 11 serial dilutions
    assay_prep.add_compound_to_assay(transfer_volume_compound=1, mixing_volume=20, compound_row=0, assay_row=12, evenodd=0)
    assay_prep.serial_dilution(evenodd=0, rangestart=13, num_of_dilutions=num_of_dilutions)

    pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+2) in 96-well compound_plate to (row+1, even) in 384-well assay_plate; then do 11 serial dilutions
    assay_prep.add_compound_to_assay(transfer_volume_compound=1, mixing_volume=20, compound_row=1, assay_row=0, evenodd=1)
    assay_prep.serial_dilution(evenodd=1, rangestart=1, num_of_dilutions=num_of_dilutions)

    pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+2) in 96-well compound plate to (row+12, even) in 384-well assay plate; then do 11 serial dilutions
    assay_prep.add_compound_to_assay(transfer_volume_compound=1, mixing_volume=20, compound_row=1, assay_row=12, evenodd=1)
    assay_prep.serial_dilution(evenodd=1, rangestart=13, num_of_dilutions=num_of_dilutions)

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
    def __init__(self, ctx, compound_plate, assay_plate, pipette, buffer, enzyme_1, enzyme_2, liquid_trash, transfer_volume_compound, transfer_volume_dilution):
        self.ctx = ctx
        self.compound_plate = compound_plate
        self.assay_plate = assay_plate
        self.pipette = pipette
        self.buffer = buffer 
        self.enzyme_1 = enzyme_1
        self.enzyme_2 = enzyme_2
        self.liquid_trash = liquid_trash
        self.transfer_volume_compound = transfer_volume_compound
        self.transfer_volume_dilution = transfer_volume_dilution       


    def fill_plate_with_buffer(self, evenodd, rangestart, rangeend):
        for row in range(rangestart, rangeend):
            self.pipette.transfer(
                20,
                self.buffer,
                self.assay_plate.rows()[evenodd][row],
                new_tip="never"
            )       

    def add_compound_to_assay(self, transfer_volume_compound, mixing_volume, compound_row, assay_row, evenodd):     
        self.pipette.transfer(
                transfer_volume_compound,
                self.compound_plate.rows()[0][compound_row],
                self.assay_plate.rows()[evenodd][assay_row],
                mix_after=(4, mixing_volume),
                new_tip="never"
        )      

        self.ctx.delay(seconds=3)  # allow pipette tips to fully void
        self.pipette.mix(4, mixing_volume)
        self.ctx.delay(seconds=3)  # allow pipette tips to fully void
        self.pipette.mix(4, mixing_volume)
        self.ctx.delay(seconds=3)  # allow pipette tips to fully void

    def serial_dilution(self, evenodd, rangestart, num_of_dilutions):
        # Dilution of samples across the 384-well flat bottom plate
        total_mixing_volume = 40

        for source, dest in zip(
                self.assay_plate.rows()[evenodd][rangestart-1:rangestart-1+num_of_dilutions],
                self.assay_plate.rows()[evenodd][rangestart:rangestart+num_of_dilutions]
        ):

            # move to southwest corner of well to mix and transfer
            source_loc_sw = source.bottom().move(Point(x=-1*dest.width/3,
                                                 y=-1*dest.length/3,
                                                 z=1.1))
            dest_loc_sw = dest.bottom().move(Point(x=-1*dest.width/3,
                                                   y=-1*dest.length/3,
                                                   z=1.1))
            dest_loc_ne = dest.bottom().move(Point(x=1*dest.width/3,
                                                   y=1*dest.length/3,
                                                   z=1.1))
            dest_loc_nw = dest.bottom().move(Point(x=-1*dest.width/3,
                                                   y=1*dest.length/3,
                                                   z=1.1))
            dest_loc_se = dest.bottom().move(Point(x=1*dest.width/3,
                                                   y=-1*dest.length/3,
                                                   z=1.1))
            self.pipette.transfer(
                self.transfer_volume_dilution,
                source.bottom(1),
                dest,

                # mix_after=(10, total_mixing_volume/1.2),

                new_tip="never"

            )

            self.pipette.mix(2, total_mixing_volume/2, dest_loc_sw)
            self.ctx.delay(seconds=2)  # allow pipette tips to fully void
            self.pipette.mix(2, total_mixing_volume/2, dest_loc_ne)
            self.ctx.delay(seconds=2)  # allow pipette tips to fully void
            self.pipette.mix(2, total_mixing_volume/2, dest_loc_nw)
            self.ctx.delay(seconds=2)  # allow pipette tips to fully void
            self.pipette.mix(2, total_mixing_volume/2, dest_loc_se)
            self.ctx.delay(seconds=2)  # allow pipette tips to fully void


  

        # Remove transfer volume from the last column of the dilution
        self.pipette.transfer(
            self.transfer_volume_dilution,
            self.assay_plate.rows()[evenodd][rangestart+num_of_dilutions-1],
            self.liquid_trash,
            new_tip="never",
            blow_out=True
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
  
