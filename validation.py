import os


def check_and_fix_json(config_json, json_defaults: dict, json_errors: dict):
    """
    Checks the json information and where there is missing information this is set to a default value
    """
    config_json['output_type'] = 'puml'
    if 'structure' not in config_json:
        config_json['structure'] = 'GuidewireStructure'
        json_defaults[len(json_defaults) + 1] = f'Defaulting structure to puml'

    if 'core_only' not in config_json:
        json_errors[len(json_errors) + 1] = 'core_only has not been set'

    if 'core_associations' not in config_json:
        json_errors[len(json_errors) + 1] = 'core_associations has not been set'

    __include_custom(config_json, json_errors)

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


def check_and_fix_json_puml(config_json, json_defaults: dict, json_errors: dict):
    """
    Checks the json information and where there is missing information this is set to a default value
    """

    __process(config_json, json_defaults)
    __plantuml(config_json, json_defaults)
    __colour(config_json, json_defaults)

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


def __process(config_json, json_defaults: dict):
    if 'one_file' not in config_json:
        config_json['one_file'] = 'true'
        json_defaults[len(json_defaults) + 1] = f'Defaulting one_file to true'

    if 'delegate_hidden' not in config_json:
        config_json['delegate_hidden'] = 'false'
        json_defaults[len(json_defaults) + 1] = f'Defaulting delegate_hidden to false'

    if 'delegate_contents' not in config_json:
        config_json['delegate_contents'] = 'true'
        json_defaults[len(json_defaults) + 1] = f'Defaulting delegate_contents to true'

    if 'entity_contents' not in config_json:
        config_json['entity_contents'] = 'true'
        json_defaults[len(json_defaults) + 1] = f'Defaulting entity_contents to true'

    if 'typelist_contents' not in config_json:
        config_json['typelist_contents'] = 'false'
        json_defaults[len(json_defaults) + 1] = f'Defaulting typelist_contents to false'

    if 'typelist_hidden' not in config_json:
        config_json['typelist_hidden'] = 'false'
        json_defaults[len(json_defaults) + 1] = f'Defaulting typelist_hidden to false'


def __plantuml(config_json, json_defaults: dict):
    if 'plantuml_theme' not in config_json:
        config_json['plantuml_theme'] = 'guidewire from https://cmscommunity.s3.eu-central-1.amazonaws.com/plant_themes'
        json_defaults[len(json_defaults) + 1] = f'Defaulting plantuml_theme to guidewire theme'
    else:
        config_json['delegate_colour'] = ''
        config_json['entity_colour'] = ''
        config_json['meta_entity_colour'] = ''
        config_json['typelist_colour'] = ''

    if 'remove_unlinked' not in config_json:
        config_json['remove_unlinked'] = 'false'
        json_defaults[len(json_defaults) + 1] = f'Defaulting remove_unlinked to false'

    if 'plantuml_limit_size' not in config_json:
        config_json['plantuml_limit_size'] = '81920'
        json_defaults[len(json_defaults) + 1] = f'Defaulting plantuml_limit_size to 81920'

    if 'diagram_format_flag' not in config_json:
        config_json['diagram_format_flag'] = '-tsvg'
        json_defaults[len(json_defaults) + 1] = f'Defaulting diagram_format_flag to -tsvg'

    if 'diagram_verbose' not in config_json:
        config_json['diagram_verbose'] = 'true'
        json_defaults[len(json_defaults) + 1] = f'Defaulting diagram_verbose to true'


def __colour(config_json, json_defaults: dict):
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


def __include_custom(config_json, json_errors: dict):
    if 'include_custom' not in config_json:
        json_errors[len(json_errors) + 1] = 'include_custom has not been set'
    else:
        if config_json['include_custom'].lower() == 'true':
            prefix_indicator = False
            suffix_indicator = False
            if 'custom_suffix' in config_json:
                suffix_indicator = True
            if 'custom_prefix' in config_json:
                prefix_indicator = True
            if suffix_indicator is False and prefix_indicator is False:
                json_errors[
                    len(json_errors) + 1] = 'custom_prefix or custom_suffix must be set when include_custom is true'
