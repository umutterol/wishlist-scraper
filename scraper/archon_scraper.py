import requests
from bs4 import BeautifulSoup
import re

ARCHON_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/overview/10/all-dungeons/this-week"
ARCHON_GEAR_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/gear-and-tier-set/10/all-dungeons/this-week#gear-tables"
ARCHON_ENCHANTS_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/enchants-and-gems/10/all-dungeons/this-week#enchants#enchants"
ARCHON_CONSUMABLES_URL_PATTERN = "https://www.archon.gg/wow/builds/{spec}/{class_}/mythic-plus/consumables/10/all-dungeons/this-week#consumables#consumables"


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
        slot = slot_tag.get_text(strip=True).upper().replace(' ', '_')
        enchants[slot] = {
            'id': item_id,
            'name': name,
            'popularity': popularity
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
            'popularity': popularity
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
            'popularity': popularity
        })
    return gems


def parse_consumables(soup):
    consumables = []
    for col_idx in [1, 2]:
        for i in range(1, 6):
            base_selector = f'#consumables > div > div.builds-best-consumables-section__columns > div:nth-child({col_idx}) > div.builds-best-consumables-section__group > div:nth-child({i}) > div > div.best-consumable-item__name > span > div'
            a_tag = soup.select_one(base_selector + ' > div.gear-icon__icon > a')
            name_tag = soup.select_one(base_selector + ' > div.gear-icon__item > div.gear-icon__item-name > a')
            if not a_tag or not name_tag:
                continue
            href = a_tag.get('href', '')
            match = re.search(r'item=(\d+)', href)
            item_id = int(match.group(1)) if match else None
            name = name_tag.get_text(strip=True)
            consumables.append({
                'id': item_id,
                'name': name
            })
    return consumables


def fetch_talent_string(soup):
    # Use the provided selector and extract href after /blizzard/
    a_tag = soup.select_one('#talents > div > div.builds-talent-tree-build-section__talent-trees > div.talent-tree.talent-tree--compact > div.talent-tree__interactions-export > a')
    if a_tag and a_tag.has_attr('href'):
        href = a_tag['href']
        idx = href.find('/blizzard/')
        if idx != -1:
            return href[idx + len('/blizzard/'):].strip()
    return ''

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

def parse_gear_slots(soup):
    gear = {}
    for slot, selector in GEAR_SLOT_SELECTORS.items():
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
            gear[slot] = items
    return gear


def fetch_archon_data(class_name, spec):
    # Fetch stats and talent string from overview page
    url = ARCHON_URL_PATTERN.format(spec=spec.lower(), class_=class_name.lower())
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}: {resp.status_code}")
        return {}
    soup = BeautifulSoup(resp.text, 'html.parser')
    stat_priority, _ = parse_stat_priority_and_talent(soup)
    talent_string = fetch_talent_string(soup)

    # Fetch items from gear-and-tier-set page
    gear_url = ARCHON_GEAR_URL_PATTERN.format(spec=spec.lower(), class_=class_name.lower())
    gear_resp = requests.get(gear_url)
    if gear_resp.status_code != 200:
        print(f"Failed to fetch {gear_url}: {gear_resp.status_code}")
        items = {}
    else:
        gear_soup = BeautifulSoup(gear_resp.text, 'html.parser')
        items = parse_gear_slots(gear_soup)

    # Fetch enchants, epic gems, and gems from enchants-and-gems page
    enchants_url = ARCHON_ENCHANTS_URL_PATTERN.format(spec=spec.lower(), class_=class_name.lower())
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
    consumables_url = ARCHON_CONSUMABLES_URL_PATTERN.format(spec=spec.lower(), class_=class_name.lower())
    consumables_resp = requests.get(consumables_url)
    if consumables_resp.status_code != 200:
        print(f"Failed to fetch {consumables_url}: {consumables_resp.status_code}")
        consumables = []
    else:
        consumables_soup = BeautifulSoup(consumables_resp.text, 'html.parser')
        consumables = parse_consumables(consumables_soup)

    # Format statprio as a string
    statprio_str = ' > '.join(stat_priority)

    # Compose the final structure
    result = {
        'talent': talent_string or '',
        'statprio': statprio_str,
        'enchants': enchants,
        'epic_gems': epic_gems,
        'gems': gems,
        'consumables': consumables,
    }
    # Add gear slots
    for slot, items_list in items.items():
        result[slot] = items_list
    return result
