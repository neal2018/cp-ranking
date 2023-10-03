import csv

filename = 'scripts/handles.csv'
out = 'src/data/handles.json'

with open(out, "w") as f:
    f.write("[\n")
    with open(filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        for i, row in enumerate(datareader):
            if i == 0:
                continue
            f.write((",\n" if i > 1 else "") + f'\t{{\n\t\t"username": "{row[0]}",\n\t\t"codeforces_handles": [\n\t\t\t"{row[1]}"\n\t\t]\n\t}}')
    f.write("\n]")