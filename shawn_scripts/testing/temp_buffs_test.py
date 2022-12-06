which_compounds = []
compound = 0
comp_row_list = ['A','B','C','D']
for row in comp_row_list:
    for i in range(1,7):
        which_compounds.append(row+str(i))
print(which_compounds)

which_rows = 0
for i in range(which_rows, which_rows+16, 2):
    print(i)
which_rows = 1
for i in range(which_rows, which_rows+16, 2):
    print(i)
