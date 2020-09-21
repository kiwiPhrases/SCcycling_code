"""
# IMLeagues Roster Scraper

IMLeagues does not provide a convenient way to download the names and e-mails of one's club. The code below is intended to help you download the roster without having to manually copy/paste names and emails. 

## To Use

Navigate to your Club's roster, click on "printable view", right-click, and Save-As the website into a convenient folder. 


Change the `data_path` to the path where you saved the website. 

Run the code. 

The code will save your roster as a CSV file in the directory where you saved the website. 
"""

# load needed libraries
from bs4 import BeautifulSoup as bs
#import requests 
import pandas as pd
import os, re


def definePaths(data_path, rostername="printablerosters.html"):
    print("Is the location of the roster here?: %s" %data_path)
    while os.path.exists("/".join([data_path, rostername])) is False:
        response = askAgain(input("..the above path doesn't exist. To change, type y. To quit type n: "))
        if response == 'y':
            data_path = input("Type new path: ")
        if response == 'n':
            break
    return(data_path)

def askAgain(response):
    while (response != 'y') & (response != 'n'):
        print("oops, try again...")
        response = input("Type y or n: ")
    return(response)

def scraperRoster(data_path, rostername):
    # read in the html file
    print("\nScraping IMLeagues roster...")
    print("\tOpening the file")
    with open("/".join([data_path, 'printablerosters.html'])) as f:
        page = f.read()
    
    # turn to soup
    print("\tCooking the soup")
    soup = bs(page,'html.parser')
    
    # find names and emails
    print("\tGetting names and emails")
    datdict = {}
    datdict['names'] = [s.text for s in  soup.find_all(id = re.compile("Name")) if 'University of Southern California' not in s.text]
    datdict['emails'] = [b.text for b in soup.find_all('td') if ('email' in b.text.lower()) & ('\n' not in b.text)]
    
    lengthCheck = (len(datdict['names']) == len(datdict['emails']))
    #print("\tAre fields of equal length? %s" %lengthCheck)
    if lengthCheck:
        # turn into dataframe
        df = pd.DataFrame(datdict)
        df.loc[:,'emails'] = df.emails.str.replace("Email\:",'')
        df.loc[:,'names'] =df.names.str.replace("\(Forms\)", '')
        
        print("\tSaved the roster to a CSV in %s" %data_path)
        df.to_csv("/".join([data_path, 'IMLeagues_roster.csv']))
    else:
        print("\tSomething is wrong, number of names doesn't equal number of e-mails")
        
def main():
    # default data path
    data_path = 'C:/Users/SpiffyApple/Documents/USC/Clubs/Cycling'
    roster_name="printablerosters.html"
    
    data_path = definePaths(data_path, roster_name)
    scraperRoster(data_path,roster_name)
    
if __name__ == '__main__':
    main()         