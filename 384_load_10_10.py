from opentrons import protocol_api
def get_values(*names):
    import json
    _all_values = json.loads("""{"pipette_type":"p20_multi_gen2","tip_type":0,"trough_type":"nest_12_reservoir_15ml","plate_type":"corning_384_wellplate_112ul_flat","dilution_factor":2,"num_of_dilutions":11,"total_mixing_volume":20,"tip_use_strategy":"never"}""")
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

    # assert that the world is the way we want it to be
    assert 'multi' in pipette_type, "wrong pipette_type"

    # turn on robot rail lights
    protocol_context.set_rail_lights(True)

    # labware
    compound_plate = protocol_context.load_labware("costar_96_wellplate_200ul", '1')
    assay_plate = protocol_context.load_labware("corning_384_wellplate_112ul_flat", '2')
    trough = protocol_context.load_labware(trough_type, '7')
    buffer = trough.wells()[0]
    enzyme = trough.wells()[1]
    liquid_trash = trough.wells()[-1]
    tip_name = 'opentrons_96_tiprack_20ul'

    tiprack = [
        protocol_context.load_labware(tip_name, slot)
        for slot in ['8']
    ]

    pipette = protocol_context.load_instrument(
        pipette_type, mount='right', tip_racks=tiprack)

    transfer_volume = total_mixing_volume/dilution_factor
    diluent_volume = total_mixing_volume - transfer_volume

    assay_prep = AssayPrep(compound_plate, assay_plate, pipette, buffer, enzyme, liquid_trash, transfer_volume)

    # Distribute buffer across the assay_plate to the the number of samples
    # And add diluent to one column after the number of samples for a blank
    pipette.pick_up_tip()
    #loop to fill left odd rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=0, rangestart=0, rangeend=12)
    #loop to fill right odd rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=0, rangestart=12, rangeend=24)
    #loop to fill left even rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=1, rangestart=0, rangeend=12)
    #loop to fill right even rows of assay_plate
    assay_prep.fill_plate_with_buffer(evenodd=1, rangestart=12, rangeend=24)

    #add extra buffer to left odd rows of assay_plate
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
    assay_prep.add_compound_to_assay(transfer_volume=1, mixing_volume=10, compound_row=0, assay_row=0, evenodd=0)
    assay_prep.serial_dilution(evenodd=0, rangestart=1, num_of_dilutions=num_of_dilutions)

    pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+1) in 96-well compound_plate to (row12+1, odd) in 384-well assay_plate; then do 11 serial dilutions
    assay_prep.add_compound_to_assay(transfer_volume=1, mixing_volume=10, compound_row=0, assay_row=12, evenodd=0)
    assay_prep.serial_dilution(evenodd=0, rangestart=13, num_of_dilutions=num_of_dilutions)

    pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+2) in 96-well compound_plate to (row+1, even) in 384-well assay_plate; then do 11 serial dilutions
    assay_prep.add_compound_to_assay(transfer_volume=1, mixing_volume=10, compound_row=1, assay_row=0, evenodd=1)
    assay_prep.serial_dilution(evenodd=1, rangestart=1, num_of_dilutions=num_of_dilutions)

    pipette.drop_tip()
    pipette.pick_up_tip()

    #move compound from column (row+2) in 96-well compound plate to (row+12, even) in 384-well assay plate; then do 11 serial dilutions
    assay_prep.add_compound_to_assay(transfer_volume=1, mixing_volume=10, compound_row=1, assay_row=12, evenodd=1)
    assay_prep.serial_dilution(evenodd=1, rangestart=13, num_of_dilutions=num_of_dilutions)

    pipette.drop_tip()

    # turn off robot rail lights
    protocol_context.set_rail_lights(False)  

class AssayPrep:
    def __init__(self, compound_plate, assay_plate, pipette, buffer, enzyme, liquid_trash, transfer_volume):
        self.compound_plate = compound_plate
        self.assay_plate = assay_plate
        self.pipette = pipette
        self.buffer = buffer 
        self.enzyme = enzyme
        self.liquid_trash = liquid_trash
        self.transfer_volume = transfer_volume        


    def fill_plate_with_buffer(self, evenodd, rangestart, rangeend):
        for row in range(rangestart, rangeend):
            self.pipette.transfer(
                10,
                self.buffer,
                self.assay_plate.rows()[evenodd][row],
                new_tip="never"
            )       

    def add_compound_to_assay(self, transfer_volume, mixing_volume, compound_row, assay_row, evenodd):     
        self.pipette.transfer(
                transfer_volume,
                self.compound_plate.rows()[0][compound_row],
                self.assay_plate.rows()[evenodd][assay_row],
                mix_after=(3, mixing_volume),
                new_tip="never"
            )       

    def serial_dilution(self, evenodd, rangestart, num_of_dilutions):
        # Dilution of samples across the 384-well flat bottom plate
        total_mixing_volume = 20
        for source, dest in zip(
                self.assay_plate.rows()[evenodd][rangestart-1:rangestart-1+num_of_dilutions],
                self.assay_plate.rows()[evenodd][rangestart:rangestart+num_of_dilutions]
        ):
            self.pipette.transfer(
                self.transfer_volume,
                source,
                dest,
                mix_after=(3, total_mixing_volume/2),
                new_tip="never"
            )       

        # Remove transfer volume from the last column of the dilution
        self.pipette.transfer(
            self.transfer_volume,
            self.assay_plate.rows()[evenodd][rangestart+num_of_dilutions-1],
            self.liquid_trash,
            new_tip="never",
            blow_out=True
        )    
  
