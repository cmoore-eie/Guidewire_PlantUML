import getopt
import json
import sys
from json import JSONDecodeError

from Structures import *
from BuildCode import BuildCode

help_str = '''

Please supply the arguments for -c
        -c, --configuration - path to the configuration file
        -h, --help - displays this text

        '''

process_errors = dict()
json_errors = dict()
json_defaults = dict()


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
        try:
            file = open(config_file)
        except FileNotFoundError:
            print(f'ERROR - The configuration file {config_file} has not been found')
            sys.exit(1)
        try:
            decoded_json = json.load(file)
            config_json = check_and_fix_json(decoded_json)
            config_json['one_file_name'] = os.path.basename(file.name).split('.')[0]
            build_structure_class = globals()[config_json['structure']]
            build_structure = build_structure_class(config_json)
            build_structure.build()
            build_types = BuildCode(config_json, build_structure.plant_structures)
            build_types.type_builder()
        except JSONDecodeError:
            print(f'ERROR - The json file {config_file} is invalid and needs correcting before use')
            sys.exit(1)


def check_and_fix_json(config_json):
    """
    Checks the json information and where there is missing information this is set to a default value
    """
    if 'one_file' not in config_json:
        config_json['one_file'] = 'true'
        json_defaults[len(json_defaults) + 1] = f'Defaulting one_file to true'

    if 'plantuml_theme' not in config_json:
        config_json['plantuml_theme'] = ''
        json_defaults[len(json_defaults) + 1] = f'Defaulting plantuml_theme to empty string'
    else:
        config_json['delegate_colour'] = ''
        config_json['entity_colour'] = ''
        config_json['meta_entity_colour'] = ''
        config_json['typelist_colour'] = ''

    if 'delegate_colour' not in config_json:
        config_json['delegate_colour'] = 'WhiteSmoke'
        json_defaults[len(json_defaults) + 1] = f'Defaulting delegate_colour to WhiteSmoke'

    if 'entity_colour' not in config_json:
        config_json['entity_colour'] = 'Coral'
        json_defaults[len(json_defaults) + 1] = f'Defaulting entity_colour to Coral'
        
    if 'meta_entity_colour' not in config_json:
        config_json['meta_entity_colour'] = 'Wheat'
        json_defaults[len(json_defaults) + 1] = f'Defaulting meta_entity_colour to Wheat'
        
    if 'typelist_colour' not in config_json:
        config_json['typelist_colour'] = 'PaleTurquoise'
        json_defaults[len(json_defaults) + 1] = f'Defaulting typelist_colour to PaleTurquoise'

    if 'remove_unlinked' not in config_json:
        config_json['remove_unlinked'] = 'false'
        json_defaults[len(json_defaults) + 1] = f'Defaulting remove_unlinked to false'

    if 'plantuml_limit_size' not in config_json:
        config_json['plantuml_limit_size'] = '81920'
        json_defaults[len(json_defaults) + 1] = f'Defaulting plantuml_limit_size to 81920'

    if 'plantuml_theme' not in config_json:
        config_json['plantuml_theme'] = ''
        json_defaults[len(json_defaults) + 1] = f'Defaulting plantuml_theme to None'

    if 'diagram_format_flag' not in config_json:
        config_json['diagram_format_flag'] = '-tsvg'
        json_defaults[len(json_defaults) + 1] = f'Defaulting diagram_format_flag to -tsvg'

    if 'diagram_verbose' not in config_json:
        config_json['diagram_verbose'] = 'true'
        json_defaults[len(json_defaults) + 1] = f'Defaulting diagram_verbose to true'

    if 'delegate_contents' not in config_json:
        json_errors[len(json_errors) + 1] = 'delegate_contents has not been set'

    if 'delegate_hidden' not in config_json:
        json_errors[len(json_errors) + 1] = 'delegate_hidden has not been set'

    if 'entity_contents' not in config_json:
        json_errors[len(json_errors) + 1] = 'entity_contents has not been set'

    if 'typelist_contents' not in config_json:
        json_errors[len(json_errors) + 1] = 'typelist_contents has not been set'

    if 'typelist_hidden' not in config_json:
        json_errors[len(json_errors) + 1] = 'typelist_hidden has not been set'

    if 'structure' not in config_json:
        json_errors[len(json_errors) + 1] = 'structure has not been set'

    if 'core_only' not in config_json:
        json_errors[len(json_errors) + 1] = 'core_only has not been set'

    if 'core_associations' not in config_json:
        json_errors[len(json_errors) + 1] = 'core_associations has not been set'

    if 'include_custom' not in config_json:
        json_errors[len(json_errors) + 1] = 'include_custom has not been set'
    else:
        if config_json['include_custom'].lower() == 'true':
            if 'custom_prefix' not in config_json:
                json_errors[len(json_errors) + 1] = 'custom_prefix must be set when include_custom is true'

    if 'source_path' in config_json:
        source_path = config_json['source_path']
        if not os.path.exists(source_path):
            json_errors[len(json_errors) + 1] = f'source_path {source_path} is invalid'
    else:
        json_errors[len(json_errors) + 1] = f'source_path has not been set'

    if 'target_path' in config_json:
        target_path = config_json['target_path']
        if not os.path.exists(target_path):
            json_errors[len(json_errors) + 1] = f'target_path {target_path} is invalid'
    else:
        json_errors[len(json_errors) + 1] = f'target_path has not been set'

    if 'generate_diagram' not in config_json:
        json_errors[len(json_errors) + 1] = 'generate_diagram has not been set'
    else:
        if config_json['generate_diagram'].lower() == 'true':
            if 'local_plantuml_jar' in config_json:
                local_plantuml_jar = config_json['local_plantuml_jar']
                if not os.path.exists(local_plantuml_jar):
                    json_errors[len(json_errors) + 1] = f'local_plantuml_jar {local_plantuml_jar} is invalid'
            else:
                json_errors[len(json_errors) + 1] = f'local_plantuml_jar has not been set'

    if len(json_errors) > 0:
        print("")
        print("Configuration issues")
        print("====================")
        for error_item in json_errors:
            print(f"({error_item}) : {json_errors[error_item]}")
        sys.exit(1)

    if len(json_defaults) > 0:
        print("")
        print("Configuration settings defaulted")
        print("================================")
        for default_item in json_defaults:
            print(f"({default_item}) : {json_defaults[default_item]}")
    return config_json


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(help_str)
        sys.exit()
    main(sys.argv[1:])
