import csv


def write_price_data_dict_csv(data: dict, source: str):
    csvfile = open(f".\\files\\{source}_price_data_compact.csv", "w", newline="")
    csvfile_raw = open(f".\\files\\{source}_price_data.csv", "w", newline="")
    compact_writer = csv.writer(
        csvfile, delimiter=";", quotechar="'", quoting=csv.QUOTE_MINIMAL
    )
    raw_writer = csv.writer(
        csvfile_raw, delimiter=";", quotechar="'", quoting=csv.QUOTE_MINIMAL
    )
    compact_writer.writerow(["Query", "Price 1", "Price 2", "Price 3"])
    raw_writer.writerow(
        ["Query"] + ["Matched name", "Price", "PRoduct link", "Shop name"] * 3
    )
    for key, value in data.items():
        compact_row = [key]
        row = [key]
        for internal_value in value:
            compact_row.append(internal_value[1])
            for elem in internal_value: row.append(elem)
        raw_writer.writerow(row)
        compact_writer.writerow(compact_row)
    csvfile.close()
    csvfile_raw.close()


def read_entries_from_csv(csv_file_path):
    """
    Read single column CSV data from a file
    @{inputs} : path
    @{returns}: array of entries
    """
    entries = []
    with open(csv_file_path, mode="r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            row_entry = ""
            if row:  # Check if the row is not empty
                split_row = []
                for col in row:
                    split_row += col.split()
                row_entry  = " ".join(split_row)
            entries.append(row_entry)
    return entries