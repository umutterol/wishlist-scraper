# WishListTracker Data Scraper

This project scrapes BiS/class/spec data from archon.gg and outputs Lua data files for the WishListTracker WoW addon.

## Features
- Scrapes all classes/specs from archon.gg
- Outputs ready-to-use Lua data files for the addon
- Designed for automation (cron, GitHub Actions, etc.)

## Setup
1. Create a Python 3 virtual environment (optional but recommended):
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install requirements:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the scraper:
   ```sh
   python run_scraper.py
   ```

## Output
- Data files are written to the `data/` folder, ready to copy into your addon.

## TODO
- Implement actual scraping logic in `scraper/archon_scraper.py`
- Implement Lua table writer in `scraper/lua_writer.py`
- Add error handling, logging, and scheduling as needed
