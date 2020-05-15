from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('table', attrs={'class':'table'}) 
    tr = table.find_all("tr") 

    temp = [] #initiating a tuple

    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
    
        period = row.find_all('td')[0].text.replace(u'\xa0', ' ')
        period = period.strip()
    
        ask = row.find_all('td')[1].text
        ask = ask.strip()
    
        bid = row.find_all('td')[2].text
        bid = bid.strip()    
    
        temp.append((period,ask,bid))
        #use the key to take information here
        #name_of_object = row.find_all(...)[0].text
        #append the needed information 
    
    temp = temp[::-1] #remove the header

    df = pd.DataFrame(temp, columns = ('Date','Kurs Jual','Kurs Beli')) #creating the dataframe
   #data wranggling -  try to change the data type to right data type
    df[['Kurs Jual','Kurs Beli']] = df[['Kurs Jual','Kurs Beli']].replace(",",".", regex=True)
    df[['Kurs Jual','Kurs Beli']] = df[['Kurs Jual','Kurs Beli']].replace(" %","", regex=True)
    df[['Kurs Jual','Kurs Beli']] = df[['Kurs Jual','Kurs Beli']].copy().astype('float64')

    df['Date'] = df['Date'].apply(lambda x: x.replace('Januari', 'January'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Februari', 'February'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Maret', 'March'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('April', 'April'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Mei', 'May'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Juni', 'June'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Juli', 'July'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Agustus', 'August'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('September', 'September'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Oktober', 'October'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('November', 'November'))
    df['Date'] = df['Date'].apply(lambda x: x.replace('Desember', 'December'))
    df['Date'] = pd.to_datetime(df['Date'])

    df['Month'] = df['Date'].dt.month_name().astype('category')

    df_month = df.drop(columns=['Date'], axis=1)
    cols = list(df_month.columns)
    cols = [cols[-1]] + cols[:-1]

    df_month = df_month[cols]

    df_month_avg = df_month.groupby("Month").mean()

    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
    df_month_avg = df_month_avg.reindex(month_order)
    df_month_avg.reset_index()
   #end of data wranggling

    return df_month_avg

@app.route("/")
def index():
    df = scrap("https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019") #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
