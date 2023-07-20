import time
import requests
import aiohttp
import asyncio
import pandas
import numpy
from zipfile import ZipFile
from io import BytesIO
from bs4 import BeautifulSoup
import re

TIMER = 30.0

async def scraper(rowDF, session, index, dataframe):
    try:
        async with session.get(url=rowDF['SOURCEURL']) as results:
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
    my_cols[0] = "EVENT_ID"
    my_cols[1] = "PUBLISH_DATE"
    my_cols[54] = "ActionGeo_CountryCode"
    my_cols[56] = "ActionGeo_Lat"
    my_cols[57] = "ActionGeo_Long"
    my_cols[60] = "SOURCEURL"
    sourceDF = pandas.read_csv(zip.open(fileName), sep="\t", header=None, names=my_cols, usecols=[0, 1, 54, 56, 57, 60])
    #print(sourceDF.info(verbose=True))
    #print(sourceDF[["EVENT_ID", "PUBLISH_DATE"]])
    return sourceDF

def main() :
    print("----Daemon Section----")

    # url of the zip containing CSV file (will update every 15 minutes)
    baseUrl = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
    
    olderDataframeUrl = " "    

    while True :
        print("Connecting to dataframe...")
        with requests.get(baseUrl) as response :
            # response is a txt, our file is [...]export.csv.zip which is after two string
            updatedDataframeUrl = response.text.split()[2]

            if (olderDataframeUrl == updatedDataframeUrl) :
                # await 15 minutes
                print("...waiting 15minutes for next dataframe")
                time.sleep(15 * 60)
                continue
            else:
                # dataframe was updated
                print("...new dataframe uploaded: ", updatedDataframeUrl)
                olderDataframeUrl = updatedDataframeUrl

                with ZipFile(BytesIO(requests.get(updatedDataframeUrl).content)) as myZip :
                    fileInsideZip = myZip.namelist()[0]
                    dataframe = extractData(myZip, fileInsideZip)

        # Cleaning dataframe section-----
        filteredDF = dataframe.dropna() # Remove rows which contain any missing values (mostly GEO info)
        filteredDF = filteredDF.drop_duplicates(subset='SOURCEURL', keep="first") # Remove duplicates urls rows (a lot of rows...)
        webstNumber = len(filteredDF)
        filteredDF = filteredDF.assign(title=numpy.nan, text=numpy.nan) # Adding new column 'title' and text filled with nan
        print(filteredDF.info(verbose=True))
        print("-------------------")

        print("----Scraper Section----")

        start = time.time()
        asyncio.run(parallelizer(filteredDF))
        end = time.time()

        filteredDF = filteredDF.dropna() # again, to remove unrechable url rows and rows with empty title
        path = "./dataframe/" + fileInsideZip.split(sep=".")[0] + ".csv"
        filteredDF.to_csv(path, sep="\t")  
        #print(filteredDF[["title"]])
        print(path)

        print("Took {} seconds to check {} websites.".format(end - start, webstNumber))
        print("Valid url entries: ", len(filteredDF))


if __name__ == "__main__":
    main()
