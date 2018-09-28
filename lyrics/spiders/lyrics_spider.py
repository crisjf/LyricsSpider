import scrapy
import re

from tutorial.items import SongItem

class SongLyricsSpider(scrapy.Spider):
    name = "songlyrics"
    allowed_domains = ["songlyrics.com"]
    start_urls = [
        "http://www.songlyrics.com/"+letter+"/" for letter in 'abcdefghijklmnopqrstuvwxyz'
    ]

    def parse(self, response):
        #http://www.songlyrics.com/a/
        for href in response.xpath('//table[@class="tracklist"]').css('a::attr(href)').extract():
            url    = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_artist)

        for href in response.xpath('//li[@class="li_pagination"]//a[not(@title="Next Page")]').css('a::attr(href)').extract():
            url    = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_)

    def parse_(self, response):
        #http://www.songlyrics.com/a/1/
        for href in response.xpath('//table[@class="tracklist"]').css('a::attr(href)').extract():
            url    = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_artist)



    def parse_artist(self,response):
        #http://www.songlyrics.com/a--lyrics/
        for song_href in response.xpath('//table[@class="tracklist"]//a').css('a::attr(href)').extract():
            url    = response.urljoin(song_href)
            yield scrapy.Request(url, callback=self.parse_song)
    
    def parse_song(self,response):
        #http://www.songlyrics.com/a/sing-a-long-lyrics/
        item = SongItem()
        for field,value in zip(response.xpath('//div[@class="pagetitle"]//p/text()').extract(),response.xpath('//div[@class="pagetitle"]//p/a/text()').extract()):
            if 'artist' in unicode(field).lower():
                item['author'] = value
            if 'genre' in unicode(field).lower():
                item['genre'] = value
            if 'album' in unicode(field).lower():
                item['album'] = value
        title = unicode(response.xpath('//title/text()').extract()[0])
        item['title']  = title[title.find('-')+1:].strip()
        item['url']    = response.url
        item['lyrics'] = unicode(''.join(response.xpath('//div[@id="songLyricsDiv-outer"]//p[@id="songLyricsDiv"]/text()').extract())).strip()
        yield item
            
#scrapy crawl songlyrics -o songs.json
#scrapy shell -s USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36" "http://www.songlyrics.com/a/sing-a-long-lyrics/"
