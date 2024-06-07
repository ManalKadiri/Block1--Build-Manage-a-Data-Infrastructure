import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json


class booking_spider(scrapy.Spider):

    name="booking"
    start_urls= ['https://www.booking.com']
    liste_villes=['Aix en Provence','Marseille','Cassis','Avignon','Saintes Maries de la mer']

# Accéder à la page de chaque ville
    def start_requests(self):
        checkin="2024-06-28"
        checkout="2024-06-30"
        url_ville_type='https://www.booking.com/searchresults.fr.html?ss={}&lang=fr&checkin={}&checkout={}&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D204'
        

        for city in self.liste_villes:
            url_ville=url_ville_type.format(city, checkin, checkout)
            yield scrapy.Request(url_ville, callback=self.parse_url_hotels, meta={'city':city, 'url_ville':url_ville})

# Obtenir les informations demandées pour chaque hôtel
    def parse_url_hotels(self, response):
        hotels=response.xpath("//h3[@class='aab71f8e4e']")

        for hotel in hotels:
            nom_hotel=hotel.xpath(".//div[contains(@class,'f6431b446c a15b38c233')]/text()").get()
            url_hotel=hotel.xpath(".//@href").get()
            yield response.follow(url_hotel, callback=self.parse_details_hotels, meta={'city':response.meta ['city'], 'nom_hotel':nom_hotel, 'url_hotel': url_hotel})

        nombre_hotels_par_page=25
        while nombre_hotels_par_page < 1000:
            url_ville_page_suivante=response.meta['url_ville'] + f"&offset={nombre_hotels_par_page}"
            yield response.follow(url_ville_page_suivante, callback=self.parse_url_hotels, meta=response.meta)
            nombre_hotels_par_page+=25


    def parse_details_hotels(self, response):
        yield{
            'city':response.meta['city'],
            'nom_hotel':response.meta['nom_hotel'],
            'url_hotel': response.meta['url_hotel'],
            'coordonnes_hotel': response.xpath("//@data-atlas-latlng").get(),
            'note_hotel':response.xpath("//div[@class='c624d7469d eb03ae5461 dab7c5c6fa a937b09340 a3214e5942 d5fd510f01 dc7f26e57f']/div[1]/text()").get(),
            'description_hotel': Selector(response).css('div.hp_desc_main_content').xpath('string()').get().strip()
        }

filename = "scraping.json"


"""if filename in os.listdir('scraping_booking/'):
        os.remove('scraping_booking/' + filename)"""



process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/97.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        filename : {"format": "json"},
    }
})

process.crawl(booking_spider)
process.start()


