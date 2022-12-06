which_compounds = []
compound = 0
comp_row_list = ['A','B','C','D']
for row in comp_row_list:
    for i in range(1,7):
        which_compounds.append(row+str(i))
print(which_compounds)
