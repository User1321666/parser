import datetime
from peewee import *
import requests
from bs4 import BeautifulSoup
from decouple import config

db = PostgresqlDatabase(database=config('db_name'),
                        user=config('db_user'),
                        password=config('db_password'),
                        host='localhost')


class Parsing(Model):
    title = CharField(max_length=200)
    date = CharField(max_length=10)
    price = CharField(max_length=20)
    image_url = TextField(null=True)

    class Meta:
        database = db


data = []


def get_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0',
        'Accept': 'application/font-woff2;q=1.0,application/font-woff;q=0.9,*/*;q=0.8'
    }
    p = 2
    page = int(input('On which page should I stop parsing?: '))

    while p < page + 1:
        url = f'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273'
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        advertisement = soup.find_all("div", class_='clearfix')

        for i in advertisement:
            i.find_all("div", class_="info")
            for j in i:
                try:
                    title = j.find("div", class_='title').text.strip()
                    price = j.find("div", class_="price").text.strip()
                    if len(j.find("span", class_="date-posted").text.strip()) > 10:
                        date = datetime.datetime.today().strftime('%d/%m/%y')
                    else:
                        date = j.find("span", class_="date-posted").text.strip()
                    image_url = i.find("img").get("data-src")
                    data.append({'title': title, 'date': date, 'price': price, 'image_url': image_url})
                except:
                    pass

        print(f'page number {p} processed =)')
        p += 1


def main():
    get_data()
    db.connect()
    db.create_tables([Parsing])
    with db.atomic():
        for apartment in data:
            Parsing.create(**apartment)


if __name__ == '__main__':
    main()