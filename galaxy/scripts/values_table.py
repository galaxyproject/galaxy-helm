
# A simple script to parse configuration parameters from the README file
# and generate a new table with the entries in the current values.yml file.
# Any existing descriptions will be added to the new table.

import sys
import yaml
import numbers

original_values = dict()
key_list = list()

# These entries typically hold dictionaries of arbitrary keys that should not
# (can not?) be documented.
special_cases = {
    'configs': 'configs.*',
    'jobs': 'jobs.rules',
    'extraFileMappings': 'extraFileMappings.*',
    'ingress.annotations': 'ingress.annotations.*'
}

# Entries that should be ignored.
ignored = []

longest_key = -1
longest_desc = -1

# Parse current entry descriptions for the README so they can be included in
# the generated table.  This code is fragile in that it relies on the entry
# name being surrounded by backticks.
def parse_readme():
    global longest_desc
    with open("../README.md") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('|') and line.find('`') > 0:
                tick1 = line.find('`')
                tick2 = line.find('`', tick1 + 1)
                if tick2 > tick1:
                    key = line[tick1+1:tick2].strip()
                    bar1 = line.find('|', tick2)
                    bar2 = line.find('|', bar1 + 1)
                    desc = line[bar1+1:bar2].strip()
                    original_values[key] = desc
                    if len(desc) > longest_desc:
                        longest_desc = len(desc)


# Prints the new table with the entries from the values.yml file.  The order
# of the entries in the table is the same as the order in the values.yml file.
def print_table():
    params = "Parameters".ljust(longest_key)
    desc = "Description".ljust(longest_desc)
    params_hr = "-".ljust(longest_key, '-')
    desc_hr =  "-".ljust(longest_desc, "-")
    print(f"| {params} | {desc} |")
    print(f"|-{params_hr}-|-{desc_hr}-|")
    for key in key_list:
        print_table_row(key)

# Prints a single row in the table.
def print_table_row(key):
    key_quoted = f"`{key}`"
    if key in original_values:
        print(f"| { key_quoted.ljust(longest_key) } | {original_values[key].ljust(longest_desc)} |")
    else:
        print(f"| {key_quoted.ljust(longest_key)} | {' '.ljust(longest_desc)} |")

def record_key(key):
    global longest_key
    if len(key) > longest_key:
        longest_key = len(key)
    key_list.append(key)

# Recursively parses entries from the values.yml file so that entry names are
# flattened.  That is:
# resource:
#   requests:
#     cpu: ...
#     memory: ...
#
# becomes:
# resource.requests.cpu
# resource.requests.memory
def parse_value(key, value, label=None):
    global longest_key
    if label is None:
        label = key
    else:
        label = label + "." + key

    if label in ignored:
        print(f"Ignoring {label}")
        return

    if label in special_cases:
        print(f"Will ignore {label} from now on")
        label = special_cases[label]
        ignored.append(label)
        record_key(label)
        return

    if isinstance(value, dict):
        for k in value:
            parse_value(k, value[k], label)
    else:
        record_key(label)


# Kicks off parsing of the values.yml file.
def parse(yaml_path):
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
        for key in data:
            value=data[key]
            parse_value(key, value)

# Entry point with very basic command line parameter parsing.
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: The path to the values.yml file must be provided.")
        print("USAGE: python values_table.py ./path/to/values.yml")
        sys.exit(1)

    parse_readme()
    parse(sys.argv[1])
    print_table()