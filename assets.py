# essentials
import pandas as pd
import time
import os
from datetime import datetime
import re
import numpy as np

# database interface/driver
import sqlite3

data_path = 'C:/Users/SpiffyApple/Documents/USC/Clubs/Cycling/SCcycling_code'
def definePaths(data_path = data_path,dbname="cycling_club_assets.db"):
    print("Program thinks database is here: %s" %data_path)
    while os.path.exists("/".join([data_path, dbname])) is False:
        response = askAgain(input("..the above path doesn't exist. To change, type y. To quit type n: "))
        if response == 'y':
            data_path = input("Type new path: ")
        if response == 'n':
            break
    return("/".join([data_path, dbname]))

#query function
def askAgain(response):
    while (response != 'y') & (response != 'n'):
        print("oops, try again...")
        response = input("Type y or n: ")
    return(response)
    
def giveOptions(options = ['add new item to assets', 'record a sale', 'mark items arrived', 'query']):
    print("Options:")
    for i,s in enumerate(options):
        print('\t',i, s)
    response = input('Enter number corresponding to item you would like: ')
    while int(response) >= len(options): #& (response.isdigit() == False):
        response = input("Try again. Select option: ")
    print("\tSuperb, you selected:", options[int(response)])
    return(options[int(response)])    
    
def accessDB(dblocation):
    print("--"*20)
    response = askAgain(input("To proceed, type y. To exit, type n: "))
    if response == 'n':
        print("exiting")
        return(None)
    if response == 'y':
        print("continuing")
        print("--"*20)

    #dblocation = "/".join([data_path, dbfile])
    #print("Presumed location of database file: %s" %dblocation)
    if os.path.exists(dblocation):
        conn =  sqlite3.connect(dblocation)
        print("Connection opened to %s" %dblocation)
        
        c = conn.cursor()
        res = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print("Available tables:",res.fetchall())
        
        choice = giveOptions()
        oneMoTime = 'y'
        while oneMoTime == 'y':
            if choice == 'add new item to assets':
                addNewItem(conn)
                
            if choice == 'record a sale':
                recordSale(conn)
                
            if choice == 'mark items arrived':
                pass
                
            if choice == 'query':
                repeatQuery(conn)
            oneMoTime = askAgain("\n\t Would you like to perform another operation? (y/n): ")
            
        conn.close()
        print("\tDB connection closed")
        
    else:
        print("Can't find database file, please check the paths.")
    


def check4numeric(f, NF):
    if f not in NF:
        resp = input("%s: " %f).strip()
    if f in NF:
        resp = input("%s: " %f).strip()
        while resp.isdigit() is False:
            print("make sure you enter a number")
            resp = input("%s: " %f).strip()
    return(resp)
    
def addNewItems(conn, table = 'assets'):
   print("Fill out each of the fields.")
   print("For sizes and prices, please type numbers (including 0)")
   print("If field not applicable, just leave blank\n")
   
   numericFields = ['XXS','XS','S','M','L','XL','XXL','XXXL','retail_price','team_price']
   sizeCols = numericFields[:8]
   
   # fetch column names
   c = conn.cursor()
   c.execute("PRAGMA table_info(%s);" %table)
   fields =  [t[1] for t in c.fetchall()]
   dataDict = {}
   
   forSale = askAgain(input("Is new item for sale? (y/n): "))
   forSale = forSale=='y'
   dataDict['not4sale'] = not forSale
   
   for f in fields:
        if forSale:
            if f not in ['en_route', 'not4sale', 'count', 'itemID', 'team_discount', 'MTB']:
                dataDict[f] = check4numeric(f,numericFields)
        if forSale is False:
            dataDict['team_discount'] = np.nan
            if f not in ['en_route', 'not4sale', 'itemID', 'team_discount', 'MTB','retail_price'] + sizeCols:
                dataDict[f] = check4numeric(f,numericFields)
                    
   # make data series                
   ni = pd.Series(dataDict)
   print("\tPlease check the fields: ")
   print(ni)
   
   # offer to fix fields
   response = askAgain(input('Would you like to fix any fields? '))
   if response == 'y':
        fields = input('Which fields would you like to fix? (separate with comma): ').replace(" ", '').split(",")
        for f in fields:
            ni[f] = input("%s: " %f)
     
   # replace missing stuff with NANs
   ni.replace("", np.nan,inplace=True)

   # fill out remaining columns
   sub = list(set(ni.index).intersection(numericFields))
   ni.loc[sub] = ni.loc[sub].astype('float')
   
   if forSale is True:
        ni.loc['count'] = ni.loc[sizeCols].sum()
   
   ni.loc['MTB'] = ('mtb' in ni.Item.lower()) | ("mtb" in ni.Description.lower())
   
   if ni['not4sale'] is False:
        ni.loc['team_discount'] = (ni.retail_price > ni.team_price)
   ni.loc['itemID'] = int(re.sub(':','',datetime.now().strftime('%H:%M:%S')))
   
   resp = askAgain(input("Add to database? (y/n): "))
   if resp == 'y':
        pd.DataFrame(ni).transpose().to_sql(table,conn, index=False, if_exists='append')
   if resp == 'n':
        return(ni)

def recordSale(conn):
   numericFields = ['XXS','XS','S','M','L','XL','XXL','XXXL','count']
   sizeCols = numericFields[:9]
   c = conn.cursor()
   
   resp = input("Would you like to [select] or [type] sold item?: ")
   while resp not in ['select', 'type']:
        print("Valid inputs: select or type...")
        resp = input("\tWould you like to [select] or [type] sold item?: ")
        
   if resp == 'select':
        options = c.execute("SELECT Item FROM assets").fetchall()
        item = giveOptions(options)[0]
   if resp == 'type':
        itemLike = input("which item got sold (ie Castelli aero bib): ").strip()
        options = c.execute("SELECT Item FROM assets WHERE Item LIKE '%{}%'".format(itemLike)).fetchall()
        print('Which of these did you want?')
        item = giveOptions(options)[0]
   
   retail = askAgain(input("\nWas this a sale to team member (team price)? (y/n): "))
   
   if retail == 'y':   
        price = 'retail_price'   
   if retail == 'n':
        price = 'team_price'
   date = datetime.now().strftime('%Y/%m/%d')     
   othersize = 'y'
   while othersize == 'y':
       size = input("What size got sold? (if size doesn't apply, type [count]): ").strip()
       while size not in sizeCols:
            print("Not a size option, try again..")
            size = input("What size got sold?: ").strip()
       print("\nHow many of this size got sold?")
       quant = int(check4numeric(size, ['sizeCols']))
       if size in sizeCols[:-1]:
           priorSize,priorCount = c.execute("SELECT %s, count FROM assets WHERE Item = '%s';" %(size,item)).fetchall()[0]
           newSize = priorSize - quant
           newCount = priorCount - quant
           print("\nUpdated size %s from %d to %d" %(size,priorSize,newSize))
           c.execute("UPDATE assets SET Item = '%s', %s = %d, count=%d WHERE Item = '%s';" %(item,size,newSize, newCount,item))
          
           if priorSize == c.execute("SELECT %s FROM assets WHERE Item = '%s';" %(size,item)).fetchall()[0][0]:
                print("Quantity didn't change")
                
           query = """
                INSERT INTO sales(itemID, Item, count, {0}, {1}, date) VALUES
                    ((SELECT itemID FROM assets WHERE assets.Item = '{2}'),
                    (SELECT Item FROM assets WHERE assets.Item = '{2}'),
                    {4},
                    {4},
                    (SELECT {1} FROM assets WHERE assets.Item = '{2}'),
                    ('{3}'))
                """.format(size, price, item, date,quant)
           c.execute(query)

       if size == 'count':
           priorCount = c.execute("SELECT count FROM assets WHERE Item = '%s';" %(item)).fetchall()[0][0]
           newCount = priorCount - quant
           print("Updated count from %d to %d" %(priorCount,newCount))
           c.execute("UPDATE assets SET Item = '%s', count=%d WHERE Item = '%s';" %(item,newCount,item))
           
           query = """
                INSERT INTO sales(itemID, Item, count, {1}, date) VALUES
                ((SELECT itemID FROM assets WHERE assets.Item = '{2}'),
                (SELECT Item FROM assets WHERE assets.Item = '{2}'),
                {4},
                (SELECT {1} FROM assets WHERE assets.Item = '{2}'),
                ('{3}')){0}
                """.format(';',price, item, date,quant)
           c.execute(query)
       conn.commit()
    
       othersize = askAgain(input("\n\tWant to update other sizes? (y/n): ")) 

def markArrived(conn, table='enRoute'):
   numericFields = ['XXS','XS','S','M','L','XL','XXL','XXXL','count']
   sizeCols = numericFields[:8]
   c = conn.cursor()
   
   resp = input("Would you like to [select] or [type] sold item?: ")
   while resp not in ['select', 'type']:
        print("Valid inputs: select or type...")
        resp = input("\tWould you like to [select] or [type] sold item?: ")
        
   if resp == 'select':
        options = c.execute("SELECT Item FROM %s" %table).fetchall()
        item = giveOptions(options)[0]
   if resp == 'type':
        itemLike = input("which item got sold (ie Castelli aero bib): ").strip()
        options = c.execute("SELECT Item FROM {0} WHERE Item LIKE '%{1}%'".format(table,itemLike)).fetchall()
        print('Which of these did you want?')
        item = giveOptions(options)[0]
   
   # get stuff from enRoute table
   enRoute = pd.read_sql("SELECT %s FROM enRoute INNER JOIN assets USING(itemID) WHERE Item == '%s';" %(",".join(['enRoute.'+s for s in sizeCols + ['itemID']]),item),conn)
   
   # get stuff from assets table
   assets = pd.read_sql("SELECT %s FROM assets WHERE Item == '%s';" %(",".join(sizeCols),item),conn)
  
   # add the two
   total = enRoute + assets
   
   # update the inventory table with totals
   query = """
        UPDATE assets SET
        {0} WHERE Item = '{1}';
        """.format(",".join(["%s = %d" %(s,v) for s,v in zip(total.columns,total.iloc[0])]), item)
   c.execute(query)
   print('updated inventory in assets')
   
   c.execute("DELETE FROM enRoute WHERE itemID = %d;" %enRoute.itemID)
   print("updated inventory in enRoute items")
   
   conn.commit()
       
def repeatQuery(conn):
    askAnother = 'y'
    while askAnother == 'y':
        try:
            query = input("\nPaste your SQlite query here: ")
            df = queryDB(query, conn)
            toSaveCSV(df)
            print("--"*30)
            askAnother = askAgain(input("Would you like to run anoter query? Type y or n: "))
            if askAnother == 'n':
                break
        except Exception as err:
            print("--"*30)
            print(err)
            tryAgain = askAgain(input("\nCorrect error and try again? Type y or n: "))
            print("--"*30)
            if tryAgain == 'y':
                askAnother = 'y'
            if tryAgain == 'n':
                break

def queryDB(query, conn):
    start_time = time.time()
    df = pd.read_sql_query(query, conn)
    print("\tthis query took: %.2fseconds " %((time.time() - start_time)))
    print("\tsize of file read in:", df.shape)
    toPrint = askAgain(input("Want to display first 10 rows of query? Type y or n: "))
    if toPrint == 'y':
        print(df.head(n=10))
    return(df)
    
def toSaveCSV(df):    
    toCSV = askAgain(input("Save query to csv? Type y or n: "))

    if toCSV == 'n':
        return(None)
    
    if toCSV == 'y':
        csvName = input("Type CSV file to export to (ie query1.csv): ")
        fpath = "/".join([data_path, csvName])
        print("Saving query in CSV to: %s" %fpath)
        df.to_csv(fpath)
        print("\tfinished saving")     
        
def main():
    dblocation = definePaths()
    accessDB(dblocation)
    
if __name__ == '__main__':
    main() 