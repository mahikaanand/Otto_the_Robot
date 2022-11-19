from opentrons import protocol_api
import time
import sys
import math


metadata = {
    'protocolName': 'Buffer screen',
    'author': 'Shawn Laursen',
    'description': '''Makes buffers from stocks in 24 well thermal module.
                      Plates mixes into 96well.
                      Titrates salt mixes in 96well.
                      Titrates protein in 384well. ''',
    'apiLevel': '2.8'
    }

def run(protocol):
    strobe(24, 8, True, protocol)
    setup(4, protocol)
    for buff in buffs:
        for mix in mixes:
            make_mix(buff, mix, protocol)
        plate_96well(buff, protocol)
        salt_titration(buff, protocol)
        protein_titration(buff, protocol)
    strobe(24, 8, False, protocol)

def strobe(blinks, hz, leave_on, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)

def setup(num_buffs, protocol):
    #equiptment
    global trough, tips300, tips300_2, plate96, plate384, p300m, tempdeck
    trough = protocol.load_labware('nest_12_reservoir_15ml', '2')
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 6)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300_2])
    tempdeck = protocol.load_module('temperature module gen2', 10)

    #buffs
    global buffs, buffa, buffb, buffc, buffd
    buffa = trough.wells()[0]
    buffb = trough.wells()[1]
    buffc = trough.wells()[2]
    buffd = trough.wells()[3]
    buffs = [buffa, buffb, buffc, buffd]
    del buffs[num_buffs:]

    #components
    global temp_buffs, high_salt, low_salt, edta, water, protein, dna, dna_extra
    temp_buffs = tempdeck.load_labware(
                 'opentrons_24_aluminumblock_nest_1.5ml_snapcap')
    high_salt = trough.wells()[4]
    low_salt = trough.wells()[5]
    edta = trough.wells()[6]
    water = trough.wells()[7]
    protein = temp_buffs.wells_by_name()['A1']
    dna = temp_buffs.wells_by_name()['A2']
    dna_extra = temp_buffs.wells_by_name()['D2']

    #mix volumes
    global hi_prot_dna_vol, lo_prot_dna_vol, hi_dna_vol, lo_dna_vol
    hi_prot_dna_vol = 150
    lo_prot_dna_vol = 350
    hi_dna_vol = 550
    lo_dna_vol = 1500

    #mixes
    global hi_prot_dna, lo_prot_dna, hi_dna, lo_dna, mixes
    hi_prot_dna = [edta, high_salt, dna, protein]
    lo_prot_dna = [edta, low_salt, dna, protein]
    hi_dna = [edta, high_salt, water, dna]
    lo_dna = [edta, low_salt, water, dna_extra]
    mixes = [hi_prot_dna, lo_prot_dna, hi_dna, lo_dna]

    #component mixes
    global hpdv1, lpdv1, hdv1, ldv1
    hpdv1 = (hi_prot_dna_vol)/5
    lpdv1 = (lo_prot_dna_vol)/5
    hdv1 = (hi_dna_vol)/5
    ldv1 = (lo_dna_vol)/5

    #single tips
    global which_tips, tip
    which_tips = []
    tip = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))

def make_mix(buff, protocol):
def plate_96well(buff, protocol):
def salt_titration(buff, protocol):
def protein_titration(buff, protocol):
