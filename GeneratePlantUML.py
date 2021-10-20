import getopt
import json
import os
import sys
from Structures import *
from BuildCode import BuildCode

help_str = '''

Please supply the arguments for -s, -t
        -c, --configuration - path to the configuration file
        -h, --help - displays this text

        '''

process_errors = dict()


def main(argv):
    config_file: str = ''

    try:
        opts, args = getopt.getopt(argv, 'c:', ['help', 'config ='])
        for opt, arg in opts:
            if opt in ['-c', '--config']:
                config_file = arg.strip()
            elif opt in ['-h', '--help']:
                print(help_str)
                sys.exit()
            else:
                sys.exit()
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)

    if config_file == '':
        process_errors[len(process_errors) +
                       1] = "-c (--config) missing and is required"
        sys.exit(1)

    if len(process_errors) > 0:
        print("")
        print("Missing Parameter Information")
        print("=============================")
        for error_item in process_errors:
            print(f"({error_item}) : {process_errors[error_item]}")
    else:
        file = open(config_file)
        config_json = json.load(file)
        build_structure_class = globals()[config_json['structure']]
        build_structure = build_structure_class(config_json)
        build_structure.build()
        build_types = BuildCode(config_json, build_structure.plant_structures)
        build_types.type_builder()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(help_str)
        sys.exit()
    main(sys.argv[1:])
