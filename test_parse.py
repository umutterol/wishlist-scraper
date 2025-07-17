from bs4 import BeautifulSoup
import re

# Sample HTML snippet (replace with your actual HTML or load from file)
html = '''
<html><body>
<div id="gear-tables">
  <div>
    <div class="builds-gear-tables-section__group">
      <div>
        <div>
          <table>
            <tbody>
              <tr>
                <td class="react-table__cell--item react-table__cell--no-wrap">
                  <span><a href="https://www.wowhead.com/item=222440"><span><span><span>Everforged Longsword</span></span></span></a></span>
                </td>
                <td class="react-table__cell--maxKey react-table__cell--no-wrap">
                  <span>+19</span>
                </td>
                <td class="react-table__cell--popularityAndReportLink react-table__cell--no-wrap">
                  <div><span>33.0%</span></div>
                </td>
              </tr>
              <tr>
                <td class="react-table__cell--item react-table__cell--no-wrap">
                  <span><a href="https://www.wowhead.com/item=228895"><span><span><span>Remixed Ignition Saber</span></span></span></a></span>
                </td>
                <td class="react-table__cell--maxKey react-table__cell--no-wrap">
                  <span>+21</span>
                </td>
                <td class="react-table__cell--popularityAndReportLink react-table__cell--no-wrap">
                  <div><span>12.4%</span></div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>
</body></html>
'''

def parse_gear_table_with_css(html):
    soup = BeautifulSoup(html, "html.parser")
    # Looser selector for test HTML
    row_selector = "table > tbody > tr"
    rows = soup.select(row_selector)
    items = []
    for row in rows:
        a_tag = row.select_one("td.react-table__cell--item.react-table__cell--no-wrap > span > a")
        item_id = None
        if a_tag and "href" in a_tag.attrs:
            href = a_tag["href"]
            if isinstance(href, str):
                m = re.search(r"item=(\\d+)", href)
                if m:
                    item_id = int(m.group(1))
        name_span = row.select_one("td.react-table__cell--item.react-table__cell--no-wrap > span > a > span > span > span")
        item_name = name_span.get_text(strip=True) if name_span else None
        pop_span = row.select_one("td.react-table__cell--popularityAndReportLink.react-table__cell--no-wrap > div > span")
        popularity = pop_span.get_text(strip=True) if pop_span else None

        items.append({
            "item_id": item_id,
            "item_name": item_name,
            "popularity": popularity,
        })
    return items

if __name__ == "__main__":
    gear = parse_gear_table_with_css(html)
    print("Parsed gear table:")
    for item in gear:
        print(item) 