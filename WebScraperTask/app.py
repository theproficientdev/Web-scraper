from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)

@app.route('/',methods = ['POST','GET'])
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/product',methods = ['POST','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        searchstring = request.form['content'].replace(" ","")

        # Connection URL
        CONNECTION_URL = f"mongodb+srv://Nik:QYmeVfVYDXOU5sQU@cluster0.vuj8o.mongodb.net/FlipkartProducts?retryWrites=true&w=majority"

        # dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
        # dataBase = dbConn['Flipkart_Products']  # connecting to the database

        DB_NAME = "FlipkartProducts"  # Specify a Database Name

        # Establish a connection with mongoDB
        client = pymongo.MongoClient(CONNECTION_URL)

        # Create a DB
        dataBase = client[DB_NAME]

        # Create a Collection Name
        # COLLECTION_NAME = searchstring
        # collection = dataBase[COLLECTION_NAME]
        products = dataBase[searchstring].find({})
        try:

            if products.count() > 0:
                return render_template('results.html',products = products)
            else:
                #page = 1

                #condition = True
                productLinks = []

                #while (condition):
                flipkart_url = "https://www.flipkart.com/search?q=" + searchstring #+ "&page=" + str(page)
                # preparing the URL to search the product on Flipkart
                uClient = uReq(flipkart_url)  # requesting the webpage from the internet
                flipkartPage = uClient.read()  # reading the webpage
                uClient.close()
                flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML

                bigboxes = flipkart_html.findAll("div", {"class": "_2kHMtA"})
                # seacrhing for appropriate tag to redirect to the product link

                for i in range(len(bigboxes)):
                    productLink = "https://www.flipkart.com" + bigboxes[i].a['href']
                    # extracting the actual product link
                    productLinks.append(productLink)
                    #if (flipkart_html.find("a", {"class": "_1LKTO3"})):
                    #    condition = True
                    #    page += 1
                    #else:
                    #    condition = False

                collection = dataBase[searchstring]
                products = []
                productNames = []
                prices = []
                averageRatings = []
                offers = []
                descriptions = []
                final_highlights = []
                for productLink in productLinks:
                    #time.sleep(1)
                    prodRes = requests.get(productLink)  # getting the product page from server
                    product_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML
                    try:
                        productName = product_html.find("span", {"class": "B_NuCI"}).text
                    except:
                        productName = "Not available"
                    productNames.append(productName)
                    try:
                        price = product_html.find("div", {"class": "_30jeq3 _16Jk6d"}).text
                    except:
                        price = "Not available"
                    prices.append(price)
                    try:
                        offer = product_html.find("div", {"class": "_3Ay6Sb _31Dcoz"}).text
                    except:
                        offer = "Not available"
                    offers.append(offer)
                    try:
                        description = product_html.find("div", {"class": "_1mXcCf RmoJUa"}).text
                    except:
                        description = "Not available"
                    descriptions.append(description)
                    highlight = ''
                    try:
                        highlights = product_html.findAll("li", {"class": "_21Ahn-"})
                        for i in range(len(highlights)):
                            highlight = highlight + highlights[i].text
                    except:
                        highlight = highlight + "Not available"
                    final_highlights.append(highlight)
                    try:
                        averageRating = product_html.find("div", {"class": "_3LWZlK"}).text
                    except:
                        averageRating = "Not available"
                    averageRatings.append(averageRating)

                    mydict = {"Product Name": productName,
                              "Price": price,
                              "Offer": offer,
                              "Average Rating": averageRating,
                              "Highlights": highlight,
                              "Description": description}  # saving that detail to a dictionary

                    x = collection.insert_one(mydict)  # inserting the dictionary containing the review comments to the collection
                    products.append(mydict)  # appending the comments to the product list

                return render_template('results.html', products=products)  # showing the products to the user

        except:
            return 'Something is wrong'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=7000,debug=True)