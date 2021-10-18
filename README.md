# Guidewire_PlantUML

This project will enable the Guidewire entity definitions to be used in creating a set of files for PlantUML. The process is controled through information in a json file.

For a more complete writeup please visit [cmoore.pl](https://chrismoore.pl/visualising-guidewire-entities/)



**python GeneratePlantUML.py -c ./plant.json**

```json
{
    "include_custom": "false",
    "custom_prefix": "_PMP",
    "source_path": "./Development/Projects/cms/cms_pc_pmp/1012",
    "target_path": "/tmp/Scratch",
    "core_only": "true",
    "delegate_colour": "WhiteSmoke",
    "entity_colour": "Coral",
    "meta_entity_colour": "Wheat",
    "typelist_contents": "false",
    "typelist_colour": "PaleTurquoise",
    "remove_unlinked": "false",
    "plantuml_limit_size": "81920",
    "generate_diagram": "true",
    "local_plantuml_jar": "/Users/XXX/Tools/PlantUML/plantuml.jar",
    "diagram_format_flag": "-tsvg",
    "core_entities": [
        {"core_entity": "PolicyPeriod"},
        {"core_entity": "Account"},
        {"core_entity": "Policy"},
        {"core_entity": "PolicyLine"},
        {"core_entity": "Cost"},
        {"core_entity": "AccountContact"},
        {"core_entity": "VirtualProduct_PMP"}
    ]
}
```



| Name                | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| Include_custom      | **true** will include entities that are prefiexed with the provided prefix in custom_prefix, **false** will not include these files specifically. |
| custom_prefix       | The prefix used for custom entities.                         |
| source_path         | The path to the Guidewire local code                         |
| target_path         | The path to where the PlantUML files will be written         |
| core_only           | setting to **true** will extract only the information for the specified core entities |
| delegate_colour     | The colour used for delegates in the generated diagram       |
| entity_colour       | The colour used for the entities in the generated diagram    |
| meta_entity_colour  | The colour used for the entities that are generated from the metadata |
| typelist_contents   | Set to **true** if the codes for the typeslists is to be included |
| typelist_colour     | The color used for typelists in the generated diagram        |
| remove_unlinked     | A setting for the generated code to remove from the generated diargam any entities that has no relationship to another entity |
| core_entities       | An array of core entity names that are used to limit the generate only if core_only is set to **true** |
| plantuml_limit_size | Override of the default size limit on the generated diagram, this may need to be adjusted depending on the size of the file and the memory available. The setting in the example will render the full set of entities and is considered the upper limit. |
| generate_diagram    | set to **true** to have the diagram generated immediately    |
| local_plantuml_jar  | path to the PlantUML jar file, PlantUML need to be installed locally for the diagram generation to work |
| diagram_format_flag | This is a flag to define the type of diagram to generate, **-tsvg** - SVG, **-tpng** - PNG |
| core_associations   | When processing core_only if this is set to **true** the immediate associations will be included |

