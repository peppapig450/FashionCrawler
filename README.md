# Web Scraper for Fashion Marketplace Sites

A Python tool for scraping multiple shopping websites such as Grailed, Depop, GOAT, and STOCKx (maybe more).

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)


## Introduction

This project aims to provide a convenient and unified interface for scraping product listings and related data from various online shopping platforms.

This originated from my AP Computer Science Principles project which was just a Grailed scraper, and I wished to expand it to more sites so I created this.
The original is [here](https://github.com/peppapig450/final-create-task-scraping).


## Project Plan

#### To-Do List / Possible Features (By Priority)

- [ ] Implement logging (TOP PRIORITY)

- [ ] Implement Depop data extraction and scraping.

- [ ] Figure out how we're gonna handle the respect scrapers. [Line 10](https://github.com/peppapig450/FashionCrawler/blob/main/main.py#L10)

- [ ] Instead of scraping Stockx for market data use their api. (maybe use go for speed)

- [ ] Options to filter the dataframe by a category

- [ ] Headless mode doesn't work if it can't be fixed -> maybe try minimized mode?

## Installation

Install using a virtual environment (recommended)

```bash
# clone repository
git clone https://github.com/peppapig450/FashionCrawler

# switch to directory
cd fashioncrawler

# setup and activate virtual environment
python3 -m venv venv && source venv/bin/activate

# install dependencies
pip install -r requirements.txt
```
