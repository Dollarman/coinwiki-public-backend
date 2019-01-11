# coinwiki-public-backend

This repo hosts the code for most of the backend powering Dollarman.com. 

Python:
* YAML parser that parses Hugo YAML frontmatter in .md files.
* Hugo file builder using the YAML parser to read and update entire wiki pages.
* PrettyPrint class without sorting the output (by default) 
* Heroku Initialization script for a new Database
* Heroku continuous update and log script for storing cryptocurrency data from Binance.
* Heroku merge remote DB with a local postgre DB. 
* SQLite continuous update and log script for storing cryptocurrency data from Binance.
* export analysis of cryptocurrencies for the past week to json files for use in Github Pages website.

Hugo:
* DocDock theme-based site, with serverless search and graphs.
* Hugo builds wiki pages entirely from YAML frontmatter which makes it possible to populate wiki from a simple YAML and Python script.

Upcoming:
* Pandas improvements
