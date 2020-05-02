# Introduction

This repository contains a database of USC Cycling Club inventory and a program called `assets.py` to operate it. Easiest way to run the program is to open up your shell, go to the directory where the repo was cloned, and type 

`python assets.py`

Should run seamlessly provided you have Numpy, Pandas, and sqlite3 modules. 

Don't forget to pull updates before running the program and push once you're done. 


# Tables:

The database contains 3 tables:

1) assets : The assets table contains all of our inventory we have in our posession at the moment
2) enRoute : This table contains items that are in the assets table but of which some quantities have not been delivered to us yet. 
3) sales : This table contains items that we sold, including the price at which they sold. 

# Operations:

You can do numerous things using the assets program. You can:


1) add new items to the assets table (ie new uniform orders or socks)
2) record sales (it'll update our inventory and sales table)
3) add items from the assets table into the enRoute table to mark something that'll arrive to our inventory
4) move items from the enRoute table to the assets table to make things that were in transit and arrived. 
5) check inventory for particular items

# Background:

I took SC Cycling's Assets.xlsx (April 2020) and dumped it to a database. Hopefully, this will make it easier for us to keep track of our inventory and also make it easier for us to record changes. Feel free to send me bugs or feature suggestions. 

# To add:

Things I'd like to add: 

a) Adding a graphical interfact would probably help some users

b) Either lock database with a password or move it to password-protected area

c) Switch from sqlite3 to another database platform that can be hosted online