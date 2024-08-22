goal: swift app hosted on heroku
* i can upload images of my receipts
* gets scanned and inventoried, compared against recipes i have saved (common recipes i use)
* shows me what recipes i can make with available materials, helps plan my grocery lists by showing missing items


structure: 
* backend.py calls config, database, image inference files to store load data from images and store to mysql
* main.py makes API using fastapi
* 
