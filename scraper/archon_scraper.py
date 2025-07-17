import requests
from bs4 import BeautifulSoup
import re
from .config import (
    ARCHON_URL_PATTERN,
    ARCHON_GEAR_URL_PATTERN,
    ARCHON_ENCHANTS_URL_PATTERN,
    ARCHON_CONSUMABLES_URL_PATTERN,
    TALENT_SELECTOR,
    GEAR_SLOT_SELECTORS,
    URL_CLASS_NAMES
)


def parse_stat_priority_and_talent(soup):
    container = soup.select_one('#stats > div > div.builds-stat-priority-section__container')
    stat_priority = []
    talent_string = None
    valid_stats = ['Strength', 'Haste', 'Crit', 'Mastery', 'Versatility', 'Vers']
    if container:
        for el in container.find_all(['span', 'div'], recursive=True):
            text = el.get_text(strip=True)
            # Only add if it's a valid stat and not already in the list
            if text in valid_stats and text not in stat_priority:
                stat_priority.append(text)
        # Talent string: look for any string containing '/blizzard/' or a long string
        for el in container.find_all(string=True, recursive=True):
            if '/blizzard/' in el:
                idx = el.find('/blizzard/')
                if idx != -1:
                    talent_string = el[idx + len('/blizzard/'):].strip()
                    break
            elif len(el.strip()) > 40 and re.match(r'^[A-Za-z0-9]+$', el.strip()):
                talent_string = el.strip()
                break
        # Fallback: look for input or code blocks
        if not talent_string:
            input_tag = container.find('input')
            if input_tag and input_tag.get('value'):
                talent_string = input_tag['value'].strip()
            else:
                code_tag = container.find('code')
                if code_tag and len(code_tag.text.strip()) > 40:
                    talent_string = code_tag.text.strip()
    return stat_priority, talent_string


def parse_items(soup):
    items_by_slot = {}
    groups = soup.select('#gear-tables > div > div.builds-gear-tables-section__group')
    for group in groups:
        slot_header = group.find('div', class_=re.compile(r'builds-gear-tables-section__slot', re.I))
        slot = slot_header.get_text(strip=True).upper().replace(" ", "_") if slot_header else 'UNKNOWN'
        wrappers = group.select('div.react-table__wrapper')
        all_items = []
        for wrapper in wrappers:
            table = wrapper.find('table')
            if not table:
                continue
            for row in table.find_all('tr')[1:6]:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue
                link = cols[0].find('a', href=re.compile(r'wowhead.com/item='))
                if not link:
                    continue
                # Try to get name from link or from a span inside
                name = link.get_text(strip=True)
                if not name:
                    span = link.find('span')
                    if span:
                        name = span.get_text(strip=True)
                match = re.search(r'item=(\d+)', link['href'])
                item_id = int(match.group(1)) if match else None
                popularity = cols[2].get_text(strip=True)
                all_items.append({
                    'id': item_id,
                    'name': name,
                    'popularity': popularity
                })
        if all_items:
            items_by_slot[slot] = all_items[:5]
    return items_by_slot


def parse_enchants(soup):
    enchants = {}
    group_selector = '#enchants > div > div.builds-best-enchants-section__group'
    group = soup.select_one(group_selector)
    if not group:
        return enchants
    for i in range(1, 10):  # Up to 9 enchants
        base_selector = f'{group_selector} > div:nth-child({i}) > div > div.builds-item-breakdown__item'
        a_tag = soup.select_one(base_selector + ' > div.builds-item-breakdown__item-name > span > a')
        name_tag = soup.select_one(base_selector + ' > div.builds-item-breakdown__item-name > span > a > span > span > span')
        pop_tag = soup.select_one(f'{group_selector} > div:nth-child({i}) > div > div.builds-item-breakdown__popularity')
        slot_tag = soup.select_one(base_selector + ' > div.builds-item-breakdown__item-description > span')
        if not a_tag or not name_tag or not pop_tag or not slot_tag:
            continue
        href = a_tag.get('href', '')
        match = re.search(r'item=(\d+)', href)
        item_id = int(match.group(1)) if match else None
        name = name_tag.get_text(strip=True)
        popularity = pop_tag.get_text(strip=True)
        slot = slot_tag.get_text(strip=True).upper().replace(' ', '_').replace('-', '')  # Remove dashes
        enchants[slot] = {
            'id': item_id,
            'name': name,
            'popularity': popularity,
            # 'icon': ...  # Icon scraping is disabled; in-game icons will be used
        }
    return enchants


def parse_epic_gems(soup):
    gems = []
    tbody = soup.select_one('#gems > div > div.react-table__wrapper > div > table > tbody')
    if not tbody:
        return gems
    rows = tbody.find_all('tr')
    for row in rows:
        item_td = row.select_one('td.react-table__cell--item.react-table__cell--no-wrap > span > div > div.gear-icon__item.gear-icon__item--has-meta > div.gear-icon__item-name > a')
        pop_td = row.select_one('td.react-table__cell--popularityAndReportLink.react-table__cell--no-wrap > div > span')
        if not item_td or not pop_td:
            continue
        href = item_td.get('href', '')
        match = re.search(r'item=(\d+)', href)
        item_id = int(match.group(1)) if match else None
        name = item_td.get_text(strip=True)
        popularity = pop_td.get_text(strip=True)
        gems.append({
            'id': item_id,
            'name': name,
            'popularity': popularity,
            # 'icon': ...  # Icon scraping is disabled; in-game icons will be used
        })
    return gems


def parse_gems(soup):
    gems = []
    # Find the wrapper div for regular gems
    wrapper = soup.select_one('#__next > div > main > div.ArchonLayout_container__IeGuk.ArchonLayout_containerWithAds__CLPYV > div.body.body--style-v3-compact > div > div > section > div > div:nth-child(3) > div > div.react-table__wrapper > div')
    if not wrapper:
        return gems
    table = wrapper.find('table')
    if not table:
        return gems
    tbody = table.find('tbody')
    if not tbody:
        return gems
    rows = tbody.find_all('tr')
    for row in rows[:5]:  # Only the first 5 gems
        item_td = row.select_one('td.react-table__cell--item.react-table__cell--no-wrap > span > div > div.gear-icon__item.gear-icon__item--has-meta > div.gear-icon__item-name > a')
        pop_td = row.select_one('td.react-table__cell--popularityAndReportLink.react-table__cell--no-wrap > div > span')
        if not item_td or not pop_td:
            continue
        href = item_td.get('href', '')
        match = re.search(r'item=(\d+)', href)
        item_id = int(match.group(1)) if match else None
        name = item_td.get_text(strip=True)
        popularity = pop_td.get_text(strip=True)
        gems.append({
            'id': item_id,
            'name': name,
            'popularity': popularity,
            # 'icon': ...  # Icon scraping is disabled; in-game icons will be used
        })
    return gems


def parse_consumables(soup):
    consumables = []
    # Select both columns of most used consumables
    columns = soup.select('#consumables > div > div.builds-best-consumables-section__columns > div')
    for col in columns:
        # Each group contains multiple consumable items
        groups = col.select('div.builds-best-consumables-section__group > div')
        for group in groups:
            name_tag = group.select_one('div.best-consumable-item__name > span > div > div.gear-icon__item > div.gear-icon__item-name > a')
            pop_tag = group.select_one('div.best-consumable-item__popularity > span')
            if not name_tag:
                continue
            href = name_tag.get('href', '')
            match = re.search(r'item=(\d+)', href)
            item_id = int(match.group(1)) if match else None
            name = name_tag.get_text(strip=True)
            popularity = pop_tag.get_text(strip=True) if pop_tag else ''
            consumables.append({
                'id': item_id,
                'name': name,
                'popularity': popularity
            })
    return consumables


def fetch_talent_string(soup):
    a_tag = soup.select_one(TALENT_SELECTOR)
    if a_tag and a_tag.has_attr('href'):
        href = a_tag['href']
        idx = href.find('/blizzard/')
        if idx != -1:
            return href[idx + len('/blizzard/'):].strip()
    return ''


def parse_gear_slots(soup, slot_selectors_override=None):
    gear = {}
    selectors = slot_selectors_override if slot_selectors_override else GEAR_SLOT_SELECTORS
    for slot, selector in selectors.items():
        slot_div = soup.select_one(selector)
        if not slot_div:
            continue
        table = slot_div.find('table')
        if not table:
            continue
        items = []
        for row in table.find_all('tr')[1:6]:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue
            link = cols[0].find('a', href=re.compile(r'wowhead.com/item='))
            if not link:
                continue
            name = link.get_text(strip=True)
            if not name:
                span = link.find('span')
                if span:
                    name = span.get_text(strip=True)
            match = re.search(r'item=(\d+)', link['href'])
            item_id = int(match.group(1)) if match else None
            popularity = cols[2].get_text(strip=True)
            items.append({
                'id': item_id,
                'name': name,
                'popularity': popularity
            })
        if items:
            norm_slot = slot.replace('-', '').replace('_', '')  # Remove dashes and underscores
            gear[norm_slot] = items
    return gear


def fetch_archon_data(class_name, spec, icon=None):
    # Use dash class name for URLs if needed
    url_class = URL_CLASS_NAMES.get(class_name, class_name)
    url_class = str(url_class)  # Ensure it's a string
    # Fetch stats and talent string from overview page
    url = ARCHON_URL_PATTERN.format(spec=spec.lower(), class_=url_class.lower())
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}: {resp.status_code}")
        return {}
    soup = BeautifulSoup(resp.text, 'html.parser')
    stat_priority, _ = parse_stat_priority_and_talent(soup)
    talent_string = fetch_talent_string(soup)

    # Fetch items from gear-and-tier-set page
    gear_url = ARCHON_GEAR_URL_PATTERN.format(spec=spec.lower(), class_=url_class.lower())
    gear_resp = requests.get(gear_url)
    if gear_resp.status_code != 200:
        print(f"Failed to fetch {gear_url}: {gear_resp.status_code}")
        items = {}
    else:
        gear_soup = BeautifulSoup(gear_resp.text, 'html.parser')
        # List of (class_name, spec.lower()) tuples to apply the remapping
        slot_selectors_override = None
        remap_specs = [
            ('warrior', 'arms'),
            ('deathknight', 'unholy'),
            ('deathknight', 'blood'),
            ('druid', 'feral'),
            ('druid', 'guardian'),
            ('hunter', 'beast-mastery'),
            ('hunter', 'marksmanship'),
            ('hunter', 'survival'),
            ('paladin', 'retribution'),
        ]
        if (class_name, spec.lower()) in remap_specs:
            slot_selectors_override = GEAR_SLOT_SELECTORS.copy()
            slot_selectors_override['TRINKET'] = GEAR_SLOT_SELECTORS['OFF_HAND']
            slot_selectors_override['RINGS'] = GEAR_SLOT_SELECTORS['TRINKET']
            slot_selectors_override['HEAD'] = GEAR_SLOT_SELECTORS['RINGS']
            slot_selectors_override['NECK'] = GEAR_SLOT_SELECTORS['HEAD']
            slot_selectors_override['SHOULDERS'] = GEAR_SLOT_SELECTORS['NECK']
            slot_selectors_override['BACK'] = GEAR_SLOT_SELECTORS['SHOULDERS']
            slot_selectors_override['CHEST'] = GEAR_SLOT_SELECTORS['BACK']
            slot_selectors_override['WRISTS'] = GEAR_SLOT_SELECTORS['CHEST']
            slot_selectors_override['HANDS'] = GEAR_SLOT_SELECTORS['WRISTS']
            slot_selectors_override['WAIST'] = GEAR_SLOT_SELECTORS['HANDS']
            slot_selectors_override['LEGS'] = GEAR_SLOT_SELECTORS['WAIST']
            slot_selectors_override['FEET'] = GEAR_SLOT_SELECTORS['LEGS']
            # Remove OFF_HAND for these specs
            if 'OFF_HAND' in slot_selectors_override:
                del slot_selectors_override['OFF_HAND']
        items = parse_gear_slots(gear_soup, slot_selectors_override)

    # Fetch enchants, epic gems, and gems from enchants-and-gems page
    enchants_url = ARCHON_ENCHANTS_URL_PATTERN.format(spec=spec.lower(), class_=url_class.lower())
    enchants_resp = requests.get(enchants_url)
    if enchants_resp.status_code != 200:
        print(f"Failed to fetch {enchants_url}: {enchants_resp.status_code}")
        enchants, epic_gems, gems = {}, [], []
    else:
        enchants_soup = BeautifulSoup(enchants_resp.text, 'html.parser')
        enchants = parse_enchants(enchants_soup)
        epic_gems = parse_epic_gems(enchants_soup)
        gems = parse_gems(enchants_soup)

    # Fetch consumables from consumables page
    consumables_url = ARCHON_CONSUMABLES_URL_PATTERN.format(spec=spec.lower(), class_=url_class.lower())
    consumables_resp = requests.get(consumables_url)
    if consumables_resp.status_code != 200:
        print(f"Failed to fetch {consumables_url}: {consumables_resp.status_code}")
        consumables = []
    else:
        consumables_soup = BeautifulSoup(consumables_resp.text, 'html.parser')
        consumables = parse_consumables(consumables_soup)

    # Format statprio as a string
    statprio_str = ' > '.join(stat_priority)

    # Compose the final structure to match data_warrior_template.lua
    result = {
        'icon': icon or '',
        'talent': talent_string or '',
        'statprio': statprio_str,
        'enchants': enchants,
        'epic_gems': epic_gems,
        'gems': gems,
    }
    # Add gear slots in the correct order, splitting FINGER/TRINKET and using MAIN_HAND/OFF_HAND
    for slot in [
        'HEAD', 'NECK', 'SHOULDERS', 'BACK', 'CHEST', 'WRISTS', 'HANDS', 'WAIST', 'LEGS', 'FEET',
        'FINGER1', 'FINGER2', 'MAIN_HAND', 'OFF_HAND', 'TRINKET1', 'TRINKET2'
    ]:
        if slot == 'MAIN_HAND' and 'MAINHAND' in items:
            result[slot] = items['MAINHAND']
        elif slot == 'OFF_HAND' and 'OFFHAND' in items:
            result[slot] = items['OFFHAND']
        elif slot.startswith('FINGER') and 'RINGS' in items:
            idx = int(slot[-1]) - 1
            result[slot] = items['RINGS'][idx*5:(idx+1)*5]
        elif slot.startswith('TRINKET') and 'TRINKET' in items:
            idx = int(slot[-1]) - 1
            result[slot] = items['TRINKET'][idx*5:(idx+1)*5]
        elif slot in items:
            result[slot] = items[slot]
        else:
            result[slot] = []
    result['consumables'] = consumables
    return result
