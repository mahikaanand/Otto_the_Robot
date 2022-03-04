from opentrons import protocol_api
def get_values(*names):
    import json
    _all_values = json.loads("""{"pipette_type":"p20_multi_gen2","tip_type":0,"trough_type":"nest_12_reservoir_15ml","plate_type":"costar_96_wellplate_200ul","dilution_factor":2,"num_of_dilutions":11,"total_mixing_volume":40,"tip_use_strategy":"never"}""")
    return [_all_values[n] for n in names]


metadata = {
    'protocolName': 'Customizable Serial Dilution',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.5'
    }

def run(protocol_context):
    [pipette_type, tip_type, trough_type, plate_type,
     dilution_factor, num_of_dilutions, total_mixing_volume,
        tip_use_strategy] = get_values(  # noqa: F821
            'pipette_type', 'tip_type', 'trough_type', 'plate_type',
            'dilution_factor', 'num_of_dilutions',
            'total_mixing_volume', 'tip_use_strategy'
        )

    # assert that the world is the way we want it to be
    assert 'multi' in pipette_type, "wrong pipette_type"

    # turn on robot rail lights
    protocol_context.set_rail_lights(True)

    # labware
    trough = protocol_context.load_labware(
        trough_type, '2')
    liquid_trash = trough.wells()[-1]
    plate = protocol_context.load_labware(
        plate_type, '3')
    tip_name = 'opentrons_96_tiprack_20ul'

    tiprack = [
        protocol_context.load_labware(tip_name, slot)
        for slot in ['1']
    ]

    pipette = protocol_context.load_instrument(
        pipette_type, mount='right', tip_racks=tiprack)

    transfer_volume = total_mixing_volume/dilution_factor
    diluent_volume = total_mixing_volume - transfer_volume

    # Distribute diluent across the plate to the the number of samples
    # And add diluent to one column after the number of samples for a blank
    pipette.transfer(
        diluent_volume,
        trough.wells()[0],
        plate.rows()[0][1:1+num_of_dilutions]
    )

    # Dilution of samples across the 96-well flat bottom plate
    if tip_use_strategy == 'never':
        pipette.pick_up_tip()

    for s, d in zip(
            plate.rows()[0][:num_of_dilutions],
            plate.rows()[0][1:1+num_of_dilutions]
    ):
        pipette.transfer(
            transfer_volume,
            s,
            d,
            mix_after=(3, total_mixing_volume/2),
            new_tip=tip_use_strategy
        )

    # Remove transfer volume from the last column of the dilution
    pipette.transfer(
        transfer_volume,
        plate.rows()[0][num_of_dilutions],
        liquid_trash,
        new_tip=tip_use_strategy,
        blow_out=True
    )

    if tip_use_strategy == 'never':
        pipette.drop_tip()

    # turn on robot rail lights
    protocol_context.set_rail_lights(True)

