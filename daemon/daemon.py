import time
from datetime import date
import requests
import aiohttp
import asyncio
import pandas
import numpy
from zipfile import ZipFile
from io import BytesIO
from bs4 import BeautifulSoup
import re
import threading

TIMER = 30.0

async def scraper(rowDF, session, index, dataframe):
    try:
        async with session.get(url=rowDF['source_url']) as results:
            resp = await results.text()

            soup = BeautifulSoup(resp, 'html.parser')

            # filtering by valid title and description
            title = soup.select_one("head title")
            description = soup.select_one('head meta[name="description"]')["content"]
            if type(title) != None and type(description) != None:

                if all(exc not in title for exc in ["ERROR", "403"]):
                    title = ' '.join(title.text.split()) # this way every space concatenation will be replace by one space
                    description = ' '.join(description.split())

                    title = re.sub("[^a-zA-Z0-9\s]+", "", title) # removing special characters except space from sentence
                    description = re.sub("[^a-zA-Z0-9\s]+", "", description)

                    text = title + " " + description # will be used by machine learning later

                    dataframe.at[index, "title"] = title
                    dataframe.at[index, "description"] = description
                    dataframe.at[index, "text"] = re.sub("[^a-zA-Z0-9\s]+", "", text)

    except Exception as e:
        # TODO: title and description will stay 'nan' and after all this procedure dataframe.dropna() again
        #print("{} => unreachable.".format(rowDF['SOURCEURL']))
        pass


async def parallelizer(dataframe) :
    conn = aiohttp.TCPConnector(limit=None) # Simultaneously opened connections limiter, None is unlimited (default is 100)
    timeout = aiohttp.ClientTimeout(total=TIMER) # Each get request have TIMER seconds (default is 5min)
    async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session :
        await asyncio.gather(*[scraper(row, session, index, dataframe) for index, row in dataframe.iterrows()])

    
def extractData(zip, fileName) :
    my_cols = [str(i) for i in range(61)] # create some col names
    my_cols[52] = "country_name"
    my_cols[53] = "country_code"
    my_cols[56] = "latitude"
    my_cols[57] = "longitude"
    my_cols[60] = "source_url"
    sourceDF = pandas.read_csv(zip.open(fileName), sep="\t", header=None, names=my_cols, usecols=[52, 53, 56, 57, 60])
    #print(sourceDF.info(verbose=True))
    #print(sourceDF[["EVENT_ID", "PUBLISH_DATE"]])
    return sourceDF

def cleanDF(dataframe) :
    filteredDF = dataframe.query("latitude != longitude")
    filteredDF = filteredDF.dropna(subset = ["country_name", "country_code", \
                                             "latitude", "longitude", "source_url"])
    filteredDF = filteredDF.drop_duplicates(subset='source_url', keep="first")
    filteredDF = filteredDF.assign(title=" ", description=" ", text=" ") # Adding new column 'title' and text filled with nan

    return filteredDF

def todaysDF(url) :
    print("____thread_1__todaysDF____")
    counter = 1

    with requests.get(url) as response :
        
        master = response.text.split()
        masterExp = [s for s in master if "export" in s]
        today = date.today().strftime("%Y%m%d")
        todaysDF = [s for s in masterExp if today in s]

        for match in todaysDF :
            with ZipFile(BytesIO(requests.get(match).content)) as myZip :
                fileInsideZip = myZip.namelist()[0]
                dataframe = extractData(myZip, fileInsideZip)
            
            # Cleaning dataframe section-----
            filteredDF = cleanDF(dataframe)
            #print(filteredDF.info(verbose=True))
            
            print("----Scraper Section----")
            asyncio.run(parallelizer(filteredDF))

            filteredDF = filteredDF.dropna() # again, to remove unrechable url rows and rows with empty title
            filename = fileInsideZip.split(sep=".")[0] # This extract the file name from url (file name will be it's timestamp)
            filteredDF["publish_date"] = filename # Create a column with fixed date value equivalent to filename from gdelt
            path = "./dataframe/" + filename + ".csv"
            filteredDF.to_csv(path, sep="\t")  
            print(f"(nRT.{counter})", path)
            counter = counter + 1
            print("Valid url entries: ", len(filteredDF))

def realtimeDF(url) :
    print("____thread_2__realtimeDF____")

    olderDataframeUrl = " "
    counter = 0

    while True :
        with requests.get(url) as response :
            # response is a txt, our file is [...]export.csv.zip which is after two string
            updatedDataframeUrl = response.text.split()[2]

            if (olderDataframeUrl == updatedDataframeUrl) :
                # await 15 minutes
                print("...waiting 15minutes for next dataframe")
                time.sleep(15 * 60)
                continue
            else:
                # dataframe was updated
                counter = counter + 1
                print("...new dataframe uploaded: ", updatedDataframeUrl)
                olderDataframeUrl = updatedDataframeUrl

                with ZipFile(BytesIO(requests.get(updatedDataframeUrl).content)) as myZip :
                    fileInsideZip = myZip.namelist()[0]
                    dataframe = extractData(myZip, fileInsideZip)

        # Cleaning dataframe section-----
        filteredDF = cleanDF(dataframe)
        #print(filteredDF.info(verbose=True))

        print("----Scraper Section----")
        asyncio.run(parallelizer(filteredDF))

        filteredDF = filteredDF.dropna() # again, to remove unrechable url rows and rows with empty title
        filename = fileInsideZip.split(sep=".")[0] # This extract the file name from url (file name will be it's timestamp)
        filteredDF["publish_date"] = filename # Create a column with fixed date value equivalent to filename from gdelt
        path = "./dataframe/" + filename + ".csv"
        filteredDF.to_csv(path, sep="\t")  
        filteredDF.info()
        print(f"(RT.{counter})", path)
        print("Valid url entries: ", len(filteredDF))



def main() :
    # url of the zip containing CSV file (master)
    masterUrl = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
    realtimeUrl = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

    t1 = threading.Thread(target=todaysDF, args=(masterUrl,))
    t2 = threading.Thread(target=realtimeDF, args=(realtimeUrl,))
    t1.start()
    t2.start()

    t1.join()
    t2.join()
            

if __name__ == "__main__":
    main()
