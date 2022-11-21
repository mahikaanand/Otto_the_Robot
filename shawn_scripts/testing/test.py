import math


def main():
    protocol = 1
    run(protocol)

def run(protocol):
    setup(4, protocol)
    for buff in buffs:
        make_mixes(buff, protocol)
        plate_96well(buff, protocol)
        salt_titration(buff, protocol)
        protein_titration(buff, protocol)

def setup(num_buffs, protocol):

    global buffs, buffa, buffb, buffc, buffd
    buffa = 'buffa'
    buffb = 'buffb'
    buffc = 'buffc'
    buffd = 'buffd'
    buffs = [buffa, buffb, buffc, buffd]
    del buffs[num_buffs:]

    global which_tips, tip
    which_tips = []
    tip = 0
    tip_row_list = ['H','G','F','E','D','C','B','A']
    for i in range(0,96):
        which_tips.append(tip_row_list[(i%8)]+str(math.floor(i/8)+1))


    #components
    global components
    high_salt = 'hi_sal'
    low_salt = 'lo_sal'
    edta = 'edta'
    water = 'water'
    protein = 'prot'
    dna = 'dna'
    dna_extra = 'dna_extra'
    components = [high_salt, low_salt, edta, water, protein, dna, dna_extra]

    #mixes
    global mixes, hpd, lpd, hd, ld
    hpd = {'comps': [edta, high_salt, dna, protein], 'vol': 150, 'loc': None}
    lpd = {'comps': [edta, low_salt, dna, protein], 'vol': 350, 'loc': None}
    hd = {'comps': [edta, high_salt, water, dna], 'vol': 550, 'loc': None}
    ld = {'comps': [edta, low_salt, water, dna_extra], 'vol': 1500, 'loc': None}
    mixes = [hpd, lpd, hd, ld]

def make_mixes(buff, protocol):
    global tip
    bc=buffs.index(buff)+2
    hpd['loc'] = 'temp_buffs.rows()[0]['+str(bc)+'].top()'
    lpd['loc'] = 'temp_buffs.rows()[1]['+str(bc)+'].top()'
    hd['loc'] = 'temp_buffs.rows()[2]['+str(bc)+'].top()'
    ld['loc'] = 'temp_buffs.rows()[3]['+str(bc)+'].top()'

    for component in components:
        print(which_tips[tip])
        tip += 1
        for mix in mixes:
            print(mix)
            if component in mix['comps']:
                print(component)
                # p300m.aspirate(mix['vol']/5, component)
                # p300m.dispense(mix['vol']/5, mix['loc'])
                # p300m.touch_tip()
                # p300m.blow_out(mix['loc'])

    print(which_tips[tip])
    tip += 1
    for mix in mixes:
        print(mix)
        print(buff)
        # p300m.aspirate(mix['vol']/5, buff)
        # p300m.dispense(mix['vol']/5, mix['loc'])
        # p300m.touch_tip()
        # p300m.blow_out(mix['loc'])

def plate_96well(buff, protocol):
    None
def salt_titration(buff, protocol):
    None
def protein_titration(buff, protocol):
    None

if __name__ == '__main__':
    main()
