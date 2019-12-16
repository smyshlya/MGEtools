import os
from classes.classes import MappingTable, IdenticalProtein
import matplotlib.pyplot as plt
import numpy as np



filename = "/Users/gera/Desktop/ICEs/tyrosine_recombinase/epsilon_15/distribution_analysis/TR_distribution/RitA/RitA.mapping_table"
directory = os.path.dirname(filename)

# here we will read the mapping table
mapping_table = MappingTable(filename)
new_array = mapping_table.parse_mapping_table()
count = 0
all_count = []
all_identical_array = []
all_identical_lens = []
all_genera = []
genera_number = {}

# here we define the plot
fig = plt.figure()
ax = fig.add_subplot(111)
Ln, = ax.plot([0, 2], color="black")
ax.set_xlim([0, len(new_array)])
plt.ion()
plt.show()

# now we will download the identical protein report (IP file)
for acc_number in new_array:
    count += 1
    identical_protein = IdenticalProtein(acc_number, directory)
    if os.path.isfile(identical_protein.file):
        pass
        # print("file ", identical_protein.file, " already exists\n")
    else:
        identical_protein.download()
    all_count.append(count)

# we open the IP file and remove all instances of the protein from the mapping table
    all_identical, genera, genera_number = identical_protein.all_accession_numbers_and_genera()
    all_identical_lens.append(len(all_identical))
    all_genera.append(len(genera))
    new_array = [x for x in new_array if x not in all_identical]
    #print(len(genera))
    if len(genera) > 2:
        print("new max! ",len(genera))
        Ln, = ax.plot([0, len(genera)], color="blue")
        print("HT detected for:", acc_number, ":", genera_number)
    Ln.set_ydata(all_genera)
    Ln.set_xdata(range(len(all_genera)))
    plt.ylabel("Number of genera")
    plt.xlabel("Index")
    plt.title("Number of genera in the protein family members")
    plt.pause(0.1)

# we report in how many genera the protein is found
