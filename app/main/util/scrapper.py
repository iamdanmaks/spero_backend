from requests import get
from bs4 import BeautifulSoup
from flask.ext.babel import gettext

from .fun import decode_result


def scrape(locale, result):
    if locale == 'en':
        return get_articles_en(decode_result(result, scrape=True))
    elif locale == 'uk':
        return get_articles_uk(decode_result(result, scrape=True))


def get_articles_en(diagnosis_result):
    articles = get(
        'https://vsearch.nlm.nih.gov/vivisimo/cgi-bin/query-meta?v%3Aproject=medlineplus&v%3Asources=medlineplus-bundle&query={}'.format(
            diagnosis_result
        )
    ).content
    soup = BeautifulSoup(articles, 'html.parser')
    print(articles)
    articles = soup.findAll('li', class_='document')
    
    results = []

    for article in articles:
        results.append(
            {
                'title': article.find('div', class_='document-header').get_text()[:-1],
                'href': article.find('span', class_='url').get_text(),
                'text': article.find('div', class_='document-body').get_text()
            }
        )
    
    print(len(articles))

    return results


def get_articles_uk(diagnosis_result):
    if diagnosis_result == 'здорове серце':
        result = [
            {
                'title': 'Серце: що нам треба їсти для його здоров\'я\
                     і від чого краще відмовитись. Поради МОЗ',
                'href': 'https://life.pravda.com.ua/health/2019/03/1/235839/',
                'text': ''
            },
            {
                'title': 'Дослідження показує: якщо ви можете відтиснутись\
                     40 разів – маєте здорове серце',
                'href': 'https://life.pravda.com.ua/health/2019/02/19/235694/',
                'text': ''
            },
            {
                'title': 'Онлайн-калькyлятори ризику допоможуть визначити,\
                     чи загрожує вам серцева хвороба в найближчі кілька років',
                'href': 'https://life.pravda.com.ua/health/2019/01/29/235347/',
                'text': ''
            },
            {
                'title': 'Назвали головну причину смертей від серцево-судинних\
                     хвороб в Україні',
                'href': 'https://life.pravda.com.ua/health/2019/01/21/235208/',
                'text': ''
            },
            {
                'title': 'Як вилікувати ваше серце: маршрут пацієнта від МОЗ',
                'href': 'https://life.pravda.com.ua"/health/2018/09/29/233371/',
                'text': ''
            },
            {
                'title': 'Чому виникають хвороби серця і як мінімізувати ризики',
                'href': 'https://life.pravda.com.ua/health/2018/09/24/233279/',
                'text': ''
            }
        ]

        return result

    articles = get(
        'https://empendium.com/ua/search?q={}'.format(
            diagnosis_result
        )
    ).content
    soup = BeautifulSoup(articles, 'html.parser')
    articles = soup.findAll('div', class_='article-content')
    print(diagnosis_result)    
    results = []

    for article in articles:
        results.append(
            {
                'title': article.find('span', class_='decorate-hover').get_text(),
                'href': article.find('a')['href'],
                'text': ''
            }
        )
    
    return results
