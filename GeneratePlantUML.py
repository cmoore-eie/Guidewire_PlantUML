import getopt
import json
import sys

from BuildTypes import BuildTypes

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
                config_file = arg
            elif opt in ['-h', '--help']:
                print(help_str)
                sys.exit()
            else:
                sys.exit()
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)

    if config_file == '':
        process_errors[len(process_errors) + 1] = "-c (--config) missing and is required"
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
        build_types = BuildTypes(config_json)
        build_types.meta_builder()
        build_types.extensions_builder()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(help_str)
        sys.exit()
    main(sys.argv[1:])
