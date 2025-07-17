CLASSES_AND_SPECS = {
    "warrior": ["protection", "arms", "fury"],
    "paladin": ["holy", "protection", "retribution"],
    "hunter": ["beast-mastery", "marksmanship", "survival"],
    "rogue": ["assassination", "outlaw", "subtlety"],
    "priest": ["discipline", "holy", "shadow"],
    "deathknight": ["blood", "frost", "unholy"],
    "shaman": ["elemental", "enhancement", "restoration"],
    "mage": ["arcane", "fire", "frost"],
    "warlock": ["affliction", "demonology", "destruction"],
    "monk": ["brewmaster", "mistweaver", "windwalker"],
    "druid": ["balance", "feral", "guardian", "restoration"],
    "demonhunter": ["havoc", "vengeance"],
    "evoker": ["devastation", "preservation", "augmentation"],
}

# Mapping for class names to use in URLs (with dashes for death-knight and demon-hunter)
URL_CLASS_NAMES = {
    "deathknight": "death-knight",
    "demonhunter": "demon-hunter",
}
ARCHON_BASE_URL = "https://www.archon.gg/class/"

# URL patterns
ARCHON_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/overview/10/all-dungeons/this-week"
ARCHON_GEAR_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/gear-and-tier-set/10/all-dungeons/this-week#gear-tables"
ARCHON_ENCHANTS_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/enchants-and-gems/10/all-dungeons/this-week#enchants#enchants"
ARCHON_CONSUMABLES_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/consumables/10/all-dungeons/this-week#consumables#consumables"

# Talent selector
TALENT_SELECTOR = '#talents > div > div.builds-talent-tree-build-section__talent-trees > div.talent-tree.talent-tree--compact > div.talent-tree__interactions-export > a'

# Gear slot selectors
GEAR_SLOT_SELECTORS = {
    'MAIN_HAND': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(1)',
    'OFF_HAND': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(2)',
    'TRINKET': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(3)',
    'RINGS': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(4)',
    'HEAD': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(5)',
    'NECK': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(6)',
    'SHOULDERS': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(7)',
    'BACK': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(8)',
    'CHEST': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(9)',
    'WRISTS': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(10)',
    'HANDS': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(11)',
    'WAIST': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(12)',
    'LEGS': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(13)',
    'FEET': '#gear-tables > div > div.builds-gear-tables-section__group > div:nth-child(14)',
}

# Enchant, gem, and consumable selectors can be added here as needed

# Icon paths for each class/spec
ICON_PATHS = {
    'deathknight': {
        'blood': 'Interface/ICONS/Spell_Deathknight_BloodPresence',
        'frost': 'Interface/ICONS/Spell_Deathknight_FrostPresence',
        'unholy': 'Interface/ICONS/Spell_Deathknight_UnholyPresence',
    },
    'demonhunter': {
        'havoc': 'Interface/ICONS/Ability_DemonHunter_SpecDPS',
        'vengeance': 'Interface/ICONS/Ability_DemonHunter_SpecTank',
    },
    'druid': {
        'balance': 'Interface/ICONS/Spell_Nature_StarFall',
        'feral': 'Interface/ICONS/Ability_Druid_CatForm',
        'guardian': 'Interface/ICONS/Ability_Racial_BearForm',
        'restoration': 'Interface/ICONS/Spell_Nature_HealingTouch',
    },
    'evoker': {
        'augmentation': 'Interface/ICONS/Invoker_Spec_DragonBronze',
        'devastation': 'Interface/ICONS/Invoker_Spec_DragonRed',
        'preservation': 'Interface/ICONS/Invoker_Spec_DragonGreen',
    },
    'hunter': {
        '"beast-mastery"': 'Interface/ICONS/Ability_Hunter_BeastTaming',
        'marksmanship': 'Interface/ICONS/Ability_Marksmanship',
        'survival': 'Interface/ICONS/Ability_Hunter_SwiftStrike',
    },
    'mage': {
        'arcane': 'Interface/ICONS/Spell_Holy_MagicalSentry',
        'fire': 'Interface/ICONS/Spell_Fire_FireBolt',
        'frost': 'Interface/ICONS/Spell_Frost_FrostBolt02',
    },
    'monk': {
        'brewmaster': 'Interface/ICONS/Spell_Monk_Brewmaster_Spec',
        'mistweaver': 'Interface/ICONS/Spell_Monk_Mistweaver_Spec',
        'windwalker': 'Interface/ICONS/Spell_Monk_Windwalker_Spec',
    },
    'paladin': {
        'holy': 'Interface/ICONS/Spell_Holy_HolyBolt',
        'protection': 'Interface/ICONS/Ability_Paladin_ShieldoftheTemplar',
        'retribution': 'Interface/ICONS/Spell_Holy_AuraOfLight',
    },
    'priest': {
        'discipline': 'Interface/ICONS/Spell_Holy_PowerWordShield',
        'holy': 'Interface/ICONS/Spell_Holy_GuardianSpirit',
        'shadow': 'Interface/ICONS/Spell_Shadow_ShadowWordPain',
    },
    'rogue': {
        'assassination': 'Interface/ICONS/Ability_Rogue_DeadlyBrew',
        'outlaw': 'Interface/ICONS/Ability_Rogue_SinisterCalling',
        'subtlety': 'Interface/ICONS/Ability_Stealth',
    },
    'shaman': {
        'elemental': 'Interface/ICONS/Spell_Nature_Lightning',
        'enhancement': 'Interface/ICONS/Spell_Shaman_ImprovedStormstrike',
        'restoration': 'Interface/ICONS/Spell_Nature_MagicImmunity',
    },
    'warlock': {
        'affliction': 'Interface/ICONS/Spell_Shadow_DeathCoil',
        'demonology': 'Interface/ICONS/Spell_Shadow_Metamorphosis',
        'destruction': 'Interface/ICONS/Spell_Shadow_RainOfFire',
    },
    'warrior': {
        'arms': 'Interface/ICONS/Ability_Warrior_SavageBlow',
        'fury': 'Interface/ICONS/Ability_Warrior_BattleShout',
        'protection': 'Interface/ICONS/Ability_Warrior_DefensiveStance',
    },
}

if __name__ == "__main__":
    # Script to extract all spec icon paths from data/*.lua files
    import glob
    import re
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    icon_dict = {}
    for lua_file in glob.glob(os.path.join(data_dir, "data_*.lua")):
        class_name = os.path.basename(lua_file)[5:-4]  # data_CLASS.lua -> CLASS
        icon_dict[class_name] = {}
        with open(lua_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Find all spec blocks and their icon lines
        for i, line in enumerate(lines):
            icon_match = re.match(r'\s*icon\s*=\s*"([^"]+)",', line)
            if icon_match:
                # Try to find the spec name (the previous non-empty, all-caps line ending with = {)
                for j in range(i-1, -1, -1):
                    prev = lines[j].strip()
                    if prev and prev.isupper() and prev.endswith('= {'):
                        spec = prev.split('=')[0].strip().lower().replace('_', '-')
                        icon_dict[class_name][spec] = icon_match.group(1)
                        break
    import pprint
    pprint.pprint(icon_dict)
