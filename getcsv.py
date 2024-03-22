"""
PROGRAM TO OBTAIN SUMMARIES FROM CSV
"""

import csv
import os

def create_csv(my_data_list):
    """Scrolls through the list looking for different .py files."""
    # Remove header
    data_list = my_data_list[1:]
    my_data_csv = [['Repository', 'File Name', 'Class', 'Start Line',
                  'End Line', 'Displacement', 'Level']]

    for i in data_list:
        if not i or len(i) < 2:
            # Skip empty or incomplete rows
            continue

        if i[1] != my_data_csv[-1][1]:
            # If the current file name is different, create a new my_data_csv entry
            my_data_csv.append(i)
            file_name = i[1]
            write_file_csv(my_data_csv, file_name)

        my_data_csv.append(i)

    # Move the file_name assignment outside of the loop if you only want to use the last file_name
    if my_data_csv and len(my_data_csv) > 1:
        file_name = my_data_csv[-1][1]
    else:
        file_name = "N/A"

    # Consider handling file_name in a way that makes sense for your use case

def write_file_csv(my_data_csv, file_name, file_csv=""):
    """Create and add data in the .csv file."""
    # Get current path
    wd = os.getcwd()
    # Create new folder
    try:
        os.mkdir(wd + "/DATA_CSV")
    except FileExistsError:
        pass
    file_name = file_name.split('.py')[0] + '.csv'
    path_file = wd + '/DATA_CSV/' + file_name
    # Create a csv with each file name
    if not file_csv:
        file_csv = open(path_file, 'w', newline='', encoding='utf-8')
        with file_csv:
            writer = csv.writer(file_csv)
            writer.writerows(my_data_csv)
    else:
        with open(path_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(my_data_csv)

def read_filecsv():
    """Read data.csv and create a list to iterate."""
    with open('data.csv', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        my_data_list = list(reader)

    create_csv(my_data_list)

if __name__ == '__main__':
    read_filecsv()
