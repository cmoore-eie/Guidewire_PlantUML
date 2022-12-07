import argparse
import json
import os
import sys

import validation
from json import JSONDecodeError
from BuildPUMLCode import BuildPUMLCode
from Structures import GuidewireStructure

version_number = '3.1.0'
help_str = '''

Please supply the arguments for -c
        -c, --config - path to the json configuration file
        -h, --help - displays this text

        '''

process_errors = dict()
json_errors = dict()
json_defaults = dict()


def main():
    print("")
    print(f"Running version - {version_number}")
    print("")
    config_file: str = ''

    uml_parser = argparse.ArgumentParser(description='Path to the json commands')
    uml_parser.add_argument('Path', metavar='path', type=str, help=help_str)
    args = uml_parser.parse_args()
    config_file = args.Path

    if not os.path.isdir(config_file) and not os.path.isfile(config_file):
        print(f'Path {config_file} is not valid')
        sys.exit()

    try:
        json_file = open(config_file)
    except FileNotFoundError:
        print(f'ERROR - The configuration file {config_file} has not been found')
        sys.exit(1)
    try:
        decoded_json = json.load(json_file)
        config_json = check_and_fix_json(decoded_json)
        config_json['one_file_name'] = os.path.basename(json_file.name).split('.')[0]
        build_structure = GuidewireStructure(config_json)
        build_structure.build()
        if config_json['output_type'].lower() == 'puml':
            build_types = BuildPUMLCode(config_json, build_structure.plant_structures)
            build_types.type_builder()
    except JSONDecodeError:
        print(f'ERROR - The json file {config_file} is invalid and needs correcting before use')
        sys.exit(1)


def check_and_fix_json(config_json):
    """
    Checks the json information and where there is missing information this is set to a default value
    """
    validation.check_and_fix_json(config_json, json_defaults, json_errors)
    validation.check_and_fix_json_puml(config_json, json_defaults, json_errors)

    if len(json_defaults) > 0:
        print("")
        print("Configuration settings defaulted")
        print("================================")
        for default_item in json_defaults:
            print(f"({default_item}) : {json_defaults[default_item]}")

    if len(json_errors) > 0:
        print("")
        print("Configuration issues")
        print("====================")
        for error_item in json_errors:
            print(f"({error_item}) : {json_errors[error_item]}")
        sys.exit(1)

    return config_json


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(help_str)
        sys.exit()
    main()
