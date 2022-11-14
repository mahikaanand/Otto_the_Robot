from opentrons import protocol_api

from opentrons.types import Point



def get_values(*names):

    import json

    _all_values = json.loads("""{"pipette_type":"p20_multi_gen2","tip_type":0,"trough_type":"nest_12_reservoir_15ml","plate_type":"corning3575_384well","dilution_factor":1.66666,"num_of_dilutions":19,"total_mixing_volume":25,"tip_use_strategy":"never"}""")

    return [_all_values[n] for n in names]





metadata = {

    'protocolName': 'Customizable Serial Dilution',

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



    # turn on robot rail lights

    protocol_context.set_rail_lights(True)



    # labware

    assay_plate = protocol_context.load_labware("corning3575_384well", '2')

    trough = protocol_context.load_labware(trough_type, '1')

    buffer = trough.wells()[0]

    reagent = trough.wells()[1]

    liquid_trash = trough.wells()[-1]

    tip_name = 'opentrons_96_tiprack_20ul'



    tiprack = [

        protocol_context.load_labware(tip_name, slot)

        for slot in ['8']

    ]



    pipette = protocol_context.load_instrument(

        pipette_type, mount='right', tip_racks=tiprack)

    pipette.flow_rate.aspirate = 6
    pipette.flow_rate.dispense = 15



    transfer_volume = total_mixing_volume/dilution_factor

    diluent_volume = total_mixing_volume - transfer_volume



    assay_prep = AssayPrep(protocol_context, assay_plate, pipette, buffer, reagent, liquid_trash, transfer_volume)



    # Distribute buffer across the assay_plate to the the number of samples

    pipette.pick_up_tip()

    #loop to fill odd rows of assay_plate

    assay_prep.fill_plate_with_buffer(evenodd=0, rangestart=1, rangeend=24)



    #do 19 serial dilutions

    assay_prep.serial_dilution(evenodd=0, rangestart=1, num_of_dilutions=num_of_dilutions)



    pipette.drop_tip()



    # Distribute reagent across the assay_plate to the the number of samples

    pipette.pick_up_tip()

    #loop to fill odd rows of assay_plate

    assay_prep.fill_plate_with_reagent(evenodd=0, rangestart=0, rangeend=24)



    pipette.drop_tip()



    # turn off robot rail lights

    protocol_context.set_rail_lights(False)



class AssayPrep:

    def __init__(self, ctx, assay_plate, pipette, buffer, reagent, liquid_trash, transfer_volume):

        self.ctx = ctx
        self.assay_plate = assay_plate

        self.pipette = pipette

        self.buffer = buffer

        self.reagent = reagent

        self.liquid_trash = liquid_trash

        self.transfer_volume = transfer_volume





    def fill_plate_with_buffer(self, evenodd, rangestart, rangeend):

        for row in range(rangestart, rangeend):

            self.pipette.transfer(

                10,

                self.buffer,

                self.assay_plate.rows()[evenodd][row],

            dest(0.7)
                new_tip="never"

            )





    def serial_dilution(self, evenodd, rangestart, num_of_dilutions):

        # Dilution of samples across the 384-well flat bottom plate

        total_mixing_volume = 20

        for source, dest in zip(

                self.assay_plate.rows()[evenodd][rangestart-1:rangestart-1+num_of_dilutions],

                self.assay_plate.rows()[evenodd][rangestart:rangestart+num_of_dilutions]

        ):

            # move to southwest corner of well to mix and transfer
            source_loc_sw = source.bottom().move(Point(x=-1*dest.width/3,
                                                 y=-1*dest.length/3,
                                                 z=1.2))
            dest_loc_sw = dest.bottom().move(Point(x=-1*dest.width/3,
                                                   y=-1*dest.length/3,
                                                   z=1.2))
            dest_loc_ne = dest.bottom().move(Point(x=1*dest.width/3,
                                                   y=1*dest.length/3,
                                                   z=1.2))
            self.pipette.transfer(

                self.transfer_volume,

                source.bottom(1),

                dest,

                # mix_after=(10, total_mixing_volume/1.2),

                new_tip="never"

            )

            self.pipette.mix(4, total_mixing_volume/1.2, dest_loc_sw)
            self.ctx.delay(seconds=3)  # allow pipette tips to fully void
            self.pipette.mix(4, total_mixing_volume/1.2, dest_loc_ne)
            self.ctx.delay(seconds=3)  # allow pipette tips to fully void




        # Remove transfer volume from the last column of the dilution

        self.pipette.transfer(

            self.transfer_volume,

            self.assay_plate.rows()[evenodd][rangestart+num_of_dilutions-1],

            self.liquid_trash,
            new_tip="never",

            blow_out=True

        )



    def fill_plate_with_reagent(self, evenodd, rangestart, rangeend):

        for row in range(rangestart, rangeend):

            self.pipette.transfer(

                10,

                self.reagent,

                self.assay_plate.rows()[evenodd][row],

                new_tip="never"

            )

