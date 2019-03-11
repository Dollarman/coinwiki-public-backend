# coinwiki-public-backend

This repo hosts the code for most of the code powering Dollarman.com. 

For privacy reasons, I use a private repo for the main code I run and export it here after cleaning my comments and credentials. **You can also view the live, Hugo-compiled html-version of the site at https://github.com/dollarman/coinwiki.** That repo is updated at least once daily with the newest data located at https://github.com/Dollarman/coinwiki/tree/master/json.

There are many different tech stacks involved so I'll describe how I use each below:

## Python:
### updatecoins.py
* Grabs 24hr change value and adds it to an sqlite database. 
* This was my first file in this project and I keep running it as a third backup in case all newer Postgre databases fail. 

### MergeHerokuToLocalPostgre.py
* Contacts my Heroku DB and queries all data newer than the latest timestamp on my local db. 
* Then adds all new data row by row to my local DB.
* Includes code to debug problems with the remote DB on Heroku such as rollback, printing logs, adding new tables, or deleting all tables.

### exportcoins.py
* Retrieves the entries from localDB from past week, cleans data, calculates percent changes and exports to json files into my static folder.
* I use pandas to clean the timestamps so they look cleaner and remove duplicates and 0-value entries across all tables.
* There are helper functions filter_DF and filter_elements to help debug by filtering the DF faster than pandas' functions.
* All values are converted to USD-equivalent to aid in comparing percent changes evenly.
* Then we calculate all possible correlations: prices vs volume, price% vs volume%, prices (pair vs pair), volumes (pair vs pair).

### updateyaml.py
* This function parses YAML on each coin's MD file and ensures they all have same features by making a dictionary with each YAML file.
* It was necessary to build my own parser for 2 reasons: other parsers throw errors at Hugo's format having two --- symbols to mark beginning and end of each yaml. Also, other parsers would ignore comments which I needed to conserve in order to re-compile the page exactly as it was before and allow comments for people to edit files easily.
* It also includes functions to easily find errors, print and edit necessary changes while comparing all coins in the repo at once. 

### pretty.py
* PrettyPrint class modified without sorting the output (by default uses the insertion order from dict).

### HerokuSetup.py
* Heroku Initialization script for a new Database. In case of disaster, this file can bootstrap a working db.

### HerokuUpdateCoins.py
* Heroku continuous update and log script for storing cryptocurrency data from Binance.
* This is the magic file that runs hourly to store info remotely.

### ClearHerokuData.py
* Merges the latest data and clears all data from the remote Heroku DB while conserving the table and column structure. 
* Useful to run once a month or so in order to stay within the Heroku free tier limit.

## Hugo:
* DocDock theme-based site, with serverless Javascript search (using lunarJS) and graphs using dygraphsJS and custom skillbars.
* Hugo builds wiki pages entirely from YAML frontmatter which makes it possible to populate wiki from a simple YAML and Python script.
* Hugo builds graph pages by checking their graphType and building the appropriate divs and javascript code. 
* The main graph topic page allows you to pick any graph type and any 2 pairs of coins to plot instantly.
* The wiki section was custom made using Hugo to format every YAML entry into a Question-Answer layout in HTML.
* Great care was taken to avoid using React or other JS frameworks and instead rely on Hugo for all formatting needs.
* Currently implementing purifyCSS into the build so that each page is rendered with a watered down truly minimized CSS and Javascript in order to improve load performance. 

## SQLite:
* The first version of this site relied on me running updatecoins.py daily (at the same hour using cron) on my own computer and store everything in an SQLite db stored on the project folder.
* SQLite had 2 great limitations that prevented me from using it further:
* First, column names and table names cannot be queried in order to adapt to dynamically changing DB design. Instead, I stored these details in separate files symbols.list and tables.list and had to update these files. Later, I opted to store them inside the db itself by dedicating a table to table names and another to symbols so I could "SELECT * FROM tables" and similarly update their values. 
* Second, Heroku does not use or allow using SQLite as the container from which the file is ran cannot update files. This meant that the SQLite.db file must be hosted someplace else that allowed API access to read and write. 

## PostgreSQL:
* Heroku forced me to learn Postgre but in the end, I prefer it for several features.
* Postgre allows querying the database's internal design such as table and column names among other info.
* Postgre includes backup and restore functions that make it safer and easier to restore from disaster. This allowed me to store full backups on Dropbox without storing the copying the entire db file.
* One setback is Postgre by default forced lowercase every table and column name, even the camel-case ones. It forced changes to my analysis code which needed to hardcode some table names and a few coin pairs to use for converting to USD values. 
