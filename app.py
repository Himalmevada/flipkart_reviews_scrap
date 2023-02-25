from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo
import pandas as pd
logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)


@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")


@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = urlopen(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll(
                "div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + \
                box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            review_data = []
            headers = ["Product, Customer Name, Rating, Heading, Comment \n"]
            review_data.append(headers)

            reviews = []
            # print(commentboxes)
            for commentbox in commentboxes:
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all(
                        'p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

                mylst = [
                    f"{searchString},{name},{rating},{commentHead},{custComment}"]
                review_data.append(mylst)

            filename = searchString + ".csv"

            # method - 1 : using files.
            with open(filename, "a") as fp:
                fp.writelines(review_data)

            # method - 2 : using pandas , create df and export df to csv file.
            # df = pd.DataFrame(reviews)
            # print(df)
            # df.to_csv(filename, index=False)

            client = pymongo.MongoClient(
                "mongodb+srv://admin:admin@cluster0.ge05dtm.mongodb.net/?retryWrites=true&w=majority")
            db = client["scraper_db"]
            coll = db["scraper_coll"]
            coll.insert_many(reviews)

            logging.info("log my final result {}".format(reviews))

            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])

        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


# Postman API :
@app.route("/review_postman", methods=['POST'])
def index_postman():
    if request.method == 'POST':
        try:
            # searchString = request.json['content']
            searchString = request.json["content"].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = urlopen(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll(
                "div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + \
                box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            reviews = []

            for commentbox in commentboxes:
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all(
                        'p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    pass

                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text

                except Exception as e:
                    pass

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

            return jsonify(reviews)

        except Exception as e:
            return 'something is wrong'


if __name__ == "__main__":
    app.run(host="0.0.0.0")
