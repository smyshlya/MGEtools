import os
from classes.classes import MappingTable, IdenticalProtein, ProteinInstance
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import time

# A python script to identify HTed proteins and analyse their genetic background. HTed proteins are the proteins that
# are present in unrelated bacteria (same protein sequence exists in different genera) and therefore are putatively
# horizontally transferred. It takes protein NCBI accession numbers (provided in the input file, see example.txt),
# creates Identical Protein (IP) record files for each of the accession numbers (stored in the "/ip" folder),
# and outputs an out.csv file with distribution of all horizontally transferred proteins. It also creates a
# distribution plot for ten most widely distributed proteins. Finally it calculates the HTrate of the dataset: number
# of horizontally transferred protein / total number of proteins.
#
# Running time for a dataset with ~35K protein accession numbers is approximately 15h on iMac.

start_time = time.time()
parser = argparse.ArgumentParser()
parser.add_argument("file", default="nothing", help="This is the input file")
parser.add_argument("--ht", default=2, help="threshold number of genera for HT detection; default is 2")
parser.add_argument("--n", default=0, help="number of proteins to retrieve from the mapping table; "
                                           "if 0 retrieves all (default)")
parser.add_argument("--api_key", default="none", help="This is your api_key to access NCBI")
args = parser.parse_args()
filename = args.file
count, count_all, count_HT = 0, 0, 0
all_count, all_identical_array, all_identical_lens, all_genera, ht_genera = [], [], [], [], []
dataframe_array, all_acc_numbers, unique, to_process, derefed = [], [], [], [], []
genera_number = {}
debug = False

# here we define input parameters: mapping table file, the only one we need for our analysis,
# HT threshold and protein number

filename = os.path.abspath(filename)
directory = os.path.dirname(filename) + "/ip"
if not os.path.isdir(directory):
    print("creating %s folder" % directory)
    os.mkdir(directory)
print("your directory is", directory)
HT_threshold = int(args.ht)  # define the criteria for Horizontal Transfer
threshold = int(args.n)  # how many proteins to process, if not defined process all of them
api_key = args.api_key
print("input file is", filename)
print("HT threshold is", HT_threshold)
print("number of proteins to look at is", threshold)
print("your api_key is", api_key)

# here we will read the mapping table
mapping_table = MappingTable(filename, threshold)
new_array = mapping_table.parse_mapping_table()
print("will process", len(new_array), "accessions..")

# now we will download the identical protein report (IP file). We try to download it only once to save computational
# time.
for acc_number in new_array:
    count_all += 1
    # check if corresponding accession number does not exist in previously processed IdenticalProtein
    identical_protein = IdenticalProtein(acc_number, directory)
    if os.path.isfile(identical_protein.file) and os.path.getsize(identical_protein.file) > 0:
        derefed.append(acc_number)
        to_process.append(acc_number)
        id_prot = IdenticalProtein(acc_number, directory)
        all_identical = id_prot.parse_identical_protein()[0]
        derefed = derefed + all_identical
        derefed = list(set(derefed))
        if debug:
            print("now derefed contains this many acc numbers:", len(derefed))
    else:
        # here we check if the acc num exists in our database of already downloaded proteins DBderef
        if acc_number not in derefed:
            derefed.append(acc_number)
            to_process.append(acc_number)
            id_prot = IdenticalProtein(acc_number, directory)
            id_prot.download(api_key)
            all_identical = id_prot.parse_identical_protein()[0]
            derefed = derefed + all_identical
            derefed = list(set(derefed))
            print("now derefed contains this many acc numbers:", len(derefed))
        else:
            try:
                if debug:
                    print(acc_number, " was already processed")
            except ValueError:
                if debug:
                    print("cant't find or download ", acc_number)

print("Total to process: ", len(to_process))
print("Initial to parse: ", len(new_array))
print("Total number of accession numbers in the dataset:", len(derefed))

# now parsing
for acc_number in to_process:
    count += 1
    identical_protein = IdenticalProtein(acc_number, directory)
    all_count.append(count)
    unique.append(acc_number)
    # we open the IP file and remove all instances of the protein from the mapping table
    try:
        all_identical, genera, genera_number, all_nucs, copy_number, nuc_start, nuc_end, nuc_strand = identical_protein.parse_identical_protein()
    except:
        print(acc_number, "is damaged")
        continue
    try:
        max_key = max(copy_number, key=copy_number.get)
        if copy_number[max_key] > 1:
            if debug:
                print("for " + acc_number + " the maximum key is " + max_key + " : " + str(
                    copy_number[max_key]) + ", genera are: " + str(genera))
    except:
        if debug:
            print("couldn't identify max for " + acc_number)
    if len(genera) > HT_threshold:
        dataframe_array.append(genera_number)
        all_acc_numbers.append(acc_number)
        ht_genera.append(len(genera))
        count_HT += 1
    all_identical_lens.append(len(all_identical))
    all_genera.append(len(genera))
    new_array = [x for x in new_array if x not in all_identical]
    print(count_all, "out of", len(new_array), " is processed", end='\r')

df = pd.DataFrame(dataframe_array, index=all_acc_numbers)
df['Total_genomes'] = df.sum(axis=1)
df['Total_genera'] = ht_genera
df.dropna(how='any', axis=1)
df['Total_genera'].plot(kind="line", rot=90)
plt.savefig("HTrate_result.svg", format='svg')
with open(filename + ".unique", 'w') as f:
    for item in unique:
        f.write("%s\n" % item)
print("total number of proteins is", count_all, "of them", count, "are unique")
print("calculated HT rate is", count_HT / count)
df.to_csv(directory + "/out.csv")
print("Total time: %s seconds" % (time.time() - start_time))
plt.show()
