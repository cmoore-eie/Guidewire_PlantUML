# Guidewire_PlantUML

This project will enable the Guidewire entity definitions to be used in creating a set of files for PlantUML. The process is controled through information in a json file.

Version 2 - Preprocesses the objects into an array to alow for better processing, this removes fk's where there is an array on the other side.
Version 1 - Initial commit of the code

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



| Name               | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| Include_custom     | **true** will include entities that are prefiexed with the provided prefix in custom_prefix, **false** will not include these files specifically. |
| custom_prefix      | The prefix used for custom entities.                         |
| source_path        | The path to the Guidewire local code                         |
| target_path        | The path to where the PlantUML files will be written         |
| core_only          | setting to **true** will extract only the information for the specified core entities |
| delegate_colour    | The colour used for delegates in the generated diagram       |
| entity_colour      | The colour used for the entities in the generated diagram    |
| meta_entity_colour | The colour used for the entities that are generated from the metadata |
| typelist_contents  | Set to **true** if the codes for the typeslists is to be included |
| typelist_colour    | The color used for typelists in the generated diagram        |
| remove_unlinked    | A setting for the generated code to remove from the generated diargam any entities that has no relationship to another entity |
| core_entities      | An array of core entity names that are used to limit the generate only if core_only is set to **true** |

