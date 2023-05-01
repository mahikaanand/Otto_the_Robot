# Import required modules
from opentrons import labware, instruments, robot

# Define labware
block = labware.load('opentrons-aluminum-block-24-ct', '1')
plate = labware.load('96-flat', '2')
tiprack300 = labware.load('opentrons-tiprack-300ul', '3')

# Define pipettes
p300 = instruments.P300_Multi(
    mount='left',
    tip_racks=[tiprack300]
)

# Define volumes and concentrations
dna_conc = 10  # µM
histone_vol = 10  # µL
rxn_vols = [10.4, 12, 28, 64]  # µL
rxn_concs = [1, 0.6, 0.3, 0.15]  # M
incubation_time = 30  # minutes

# Define functions for each step
def add_dna():
    for i in range(12):
        tip = tiprack300.wells()[i]
        p300.pick_up_tip(tip)
        p300.transfer(
            dna_conc * histone_vol / 1000,  # µL -> nM
            plate.wells()[i].top(),
            mix_before=(3, 50),
            new_tip='never'
        )
        p300.mix(3, 100, plate.wells()[i])
        p300.drop_tip(tip)

def add_histone(concentration):
    histone_vol_nM = histone_vol * concentration / 1000  # µL -> nM
    for i in range(0, 8):
        tip = tiprack300.wells()[i]
        p300.pick_up_tip(tip)
        p300.transfer(
            histone_vol_nM,
            block.wells()[i].top(),
            mix_before=(3, 50),
            new_tip='never'
        )
        p300.mix(3, 100, block.wells()[i])
        p300.transfer(
            block.wells()[i+8].bottom(),
            block.wells()[i].top(),
            new_tip='never'
        )
        p300.mix(3, 100, block.wells()[i])
        p300.drop_tip(tip)

def add_rxn_buffer(volume):
    for i in range(12):
        tip = tiprack300.wells()[i]
        p300.pick_up_tip(tip)
        p300.transfer(
            volume,
            plate.wells()[i].top(),
            new_tip='never'
        )
        p300.mix(3, 100, plate.wells()[i])
        p300.drop_tip(tip)

# Perform the protocol
robot.home()  # Move the robot to the home position
add_dna()
for concentration, volume in zip(rxn_concs, rxn_vols):
    add_histone(concentration)
    robot._driver.run_flag.wait()
    robot.comment(f'Incubating for {incubation_time} minutes...')
    robot.pause(minutes=incubation_time)
    add_rxn_buffer(volume)
    robot._driver.run_flag.wait()
    robot.comment(f'Incubating for {incubation_time} minutes...')
    robot.pause(minutes=incubation_time)
