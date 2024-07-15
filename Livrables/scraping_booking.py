import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json


class booking_spider(scrapy.Spider):

    name="booking"
    start_urls= ['https://www.booking.com']
    liste_villes=['Marseille', 'Cassis', 'Lille', 'Rouen', 'Amiens']

# Accéder à la page de chaque ville
    def start_requests(self):
        checkin="2024-06-28"
        checkout="2024-06-30"
        url_ville_type='https://www.booking.com/searchresults.fr.html?ss={}&lang=fr&checkin={}&checkout={}&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D204'
        

        for city in self.liste_villes: #Pour chaque ville de la liste, formatte l'URL de recherche et crée une requête Scrapy
            url_ville=url_ville_type.format(city, checkin, checkout)
            yield scrapy.Request(url_ville, callback=self.parse_url_hotels, meta={'city':city, 'url_ville':url_ville}) #Envoie une requête pour chaque ville avec les métadonnées city et url_ville.

# Obtenir les informations demandées pour chaque hôtel
    def parse_url_hotels(self, response):
        hotels=response.xpath("//h3[@class='bdbc4ed9de']") #Sélectionne tous les éléments h3 avec la classe bdbc4ed9de, représentant les hôtels.

        for hotel in hotels:
            nom_hotel=hotel.xpath(".//div[contains(@class,'fa4a3a8221 b121bc708f')]/text()").get() 
            url_hotel=hotel.xpath(".//@href").get() 
            yield response.follow(url_hotel, callback=self.parse_details_hotels, meta={'city':response.meta ['city'], 'nom_hotel':nom_hotel, 'url_hotel': url_hotel}) #Suivre le lien de l'hôtel et appeler parse_details_hotels pour extraire plus de détails.

        nombre_hotels_par_page=25 #Initialise le nombre d'hôtels par page.
        while nombre_hotels_par_page < 1000: #Boucle pour parcourir les pages suivantes tant que moins de 1000 hôtels sont visités.
            url_ville_page_suivante=response.meta['url_ville'] + f"&offset={nombre_hotels_par_page}"
            yield response.follow(url_ville_page_suivante, callback=self.parse_url_hotels, meta=response.meta) #Suivre le lien de la page suivante et rappeler parse_url_hotels.
            nombre_hotels_par_page+=25 #URL de la page suivante.


    def parse_details_hotels(self, response):
        yield{    #Retourne un dictionnaire contenant les éléments ci-dessous
            'city':response.meta['city'],
            'nom_hotel':response.meta['nom_hotel'],
            'url_hotel': response.meta['url_hotel'],
            'coordonnes_hotel': response.xpath("//@data-atlas-latlng").get(),
            'note_hotel':response.xpath("//div[@class='da2b81213f ee0c2e82cd ba88e720cd cfe5c03925 c6381d692a b82ce43264 d203792b7e']/div[1]/text()").get(),
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


