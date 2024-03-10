# Grailed Scraper for AP CSP Final Create Task

## Description

This Python script is designed to scrape product listings from the Grailed marketplace.
It allows users to search for items based on a keyword and retrieve information such as
prices, titles, designers, sizes, and more, and save it in their preferred file format.


### Requirements
---
- Python 3.8+
- Works on macOS, Linux

---
## Project Plan

#### To-Do List
- [X] Pass search term to program via command line or ~~pop-up~~ input.
- [X] Beautiful soup to parse the prices.
- [X] Output in either csv or json.
- [ ] Scrape links to the items and pictures of them.


#### Branches
---
- **main**:
    - Contains the working single file approach.
    - Stable version with basic functionality implemented.
    - Primary development branch for the main functionality.

- **modulization-to-the-max**:
    - Utilizes modularization with 4 files imported into a main.py.
    - Experimenting with modular structure for better code organization.
    - Focuses on maximizing code modularization for easier maintenance.

- **v2**:
    - Work in progress towards an object-oriented approach.
    - Developing a new version with an object-oriented design.
    - Objective is to add additional sites to scrape using an object-oriented approach.


#### Future Posibilites
---
Beyond the AP test I may develop this into a full scaled project capable of scraping multiple sites.
This seems like a good way to get better at Python, and Web Scraping/HTML understanding.
