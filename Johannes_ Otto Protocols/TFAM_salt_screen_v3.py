from opentrons import protocol_api

metadata = {
    'protocolName': 'Salt dependency screen for TFAM',
    'author': 'Sashi',
    'source': 'Protocol Library',
    'apiLevel': '2.5'
    }

def run(protocol_context):

    protocol_context.set_rail_lights(True)

    # labware
    sample_plate = protocol_context.load_labware("costar_96_wellplate_200ul", 1)
    #tfam_samples = [sample_plate.rows(x) for x in range(0,2)]
    tfam_samples_odd = sample_plate.rows()[0][0]
    tfam_samples_even = sample_plate.rows()[0][1]
    dna_samples = sample_plate.rows()[0][2]
    assay_plate = protocol_context.load_labware("corning3575_384well_alt", 2)
    trough = protocol_context.load_labware("axygen_12_reservoir_5000ul", 3)
    salt_trough = [trough.wells(x) for x in range(0,12)]
    tiprack = [protocol_context.load_labware('opentrons_96_tiprack_20ul', 7)]
    pipette = protocol_context.load_instrument("p20_multi_gen2", mount='right', tip_racks=tiprack)

    pipette.pick_up_tip()

    salt_screen = SaltScreen(protocol_context, assay_plate, pipette)

    # fill both halves of the plate with buffer. odds first and then evens
    for i in range(0,12):
        salt_screen.fill_plate_with_buffer(salt=salt_trough[i], assay_row=i, evenodd=0) 
        salt_screen.fill_plate_with_buffer(salt=salt_trough[i], assay_row=i+12, evenodd=0)
        salt_screen.fill_plate_with_buffer(salt=salt_trough[i], assay_row=i, evenodd=1) 
        salt_screen.fill_plate_with_buffer(salt=salt_trough[i], assay_row=i+12, evenodd=1)

    pipette.drop_tip()

    # fill plate with TFAM dilutions from 96-well plate. fill both halves of the plate, odds first and then evens
    pipette.pick_up_tip()

    for i in range(0,12):
        salt_screen.add_tfam_to_assay(tfam_samples=tfam_samples_odd, assay_row=i, evenodd=1)
        salt_screen.add_tfam_to_assay(tfam_samples=tfam_samples_even, assay_row=i+12, evenodd=1)
        salt_screen.add_tfam_to_assay(tfam_samples=tfam_samples_odd, assay_row=i, evenodd=0)
        salt_screen.add_tfam_to_assay(tfam_samples=tfam_samples_even, assay_row=i+12, evenodd=0)

    pipette.drop_tip()

    # fill plate with DNA from 96-well plate. fill both halves of the plate, odds first and then evens
    pipette.pick_up_tip()

    for i in range(0,12):
        salt_screen.add_dna_to_assay(dna_samples=dna_samples, assay_row=i, evenodd=1)
        salt_screen.add_dna_to_assay(dna_samples=dna_samples, assay_row=i+12, evenodd=1)
        salt_screen.add_dna_to_assay(dna_samples=dna_samples, assay_row=i, evenodd=0)
        salt_screen.add_dna_to_assay(dna_samples=dna_samples, assay_row=i+12, evenodd=0)

    pipette.drop_tip()

    # turn off robot rail lights
    protocol_context.set_rail_lights(False)


class SaltScreen:

    def __init__(self, ctx, assay_plate, pipette):
        self.ctx = ctx
        self.assay_plate = assay_plate
        self.pipette = pipette

    def fill_plate_with_buffer(self, salt, assay_row, evenodd):
            self.pipette.transfer(
            16,
            salt,
            self.assay_plate.rows()[evenodd][assay_row],
            new_tip='never'
            )

    def add_tfam_to_assay(self, tfam_samples, assay_row, evenodd):     
            self.pipette.transfer(
            2,
            tfam_samples,
            self.assay_plate.rows()[evenodd][assay_row],
            new_tip='never'
            )

    def add_dna_to_assay(self, dna_samples, assay_row, evenodd):
            self.pipette.transfer(
            2,
            dna_samples,
            self.assay_plate.rows()[evenodd][assay_row],
            new_tip='never'
            )