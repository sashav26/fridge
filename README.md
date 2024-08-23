goal: swift app hosted on supabase
* i can upload images of my receipts
* gets scanned and inventoried, compared against recipes i have saved (common recipes i use)
* shows me what recipes i can make with available materials, helps plan my grocery lists by showing missing items
* maybe budgeting?


structure: 
* backend.py calls config, database, image inference files to extract data from receipt images and store to mysql
* main.py makes API using fastapi and sql queries
* swift app wireframe half-done, working on new features rn

what works so far:
* fastapi, backend works
* swift basic image upload functional


working on:
* backend gives me output of exact titles, not ingredient types --> mini 4o model to analyze text data, maybe OCR for processing?
* swift wireframing
* algorithms, hashmaps for speed
* UX bottleneck at quantity inputting --> maybe NLP fixes quantities too?
* is not hosted to heroku because my wifi is slow and heroku CLI taking forever rn
  
