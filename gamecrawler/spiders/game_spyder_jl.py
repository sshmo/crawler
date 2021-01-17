import scrapy
from scrapy_selenium import SeleniumRequest


class GamesSpider(scrapy.Spider):

    name = "games_jl"

    def start_requests(self):
        urls = [
            'https://play.google.com/store/apps/collection/cluster?clp=0g4YChYKEHRvcGdyb3NzaW5nX0dBTUUQBxgD:S:ANO1ljLhYwQ&gsr=ChvSDhgKFgoQdG9wZ3Jvc3NpbmdfR0FNRRAHGAM%3D:S:ANO1ljIKta8',
        ]
        for url in urls:
            yield SeleniumRequest(url=url,
                                  callback=self.parse,
                                  # https://stackoverflow.com/a/12792245
                                  script='window.scrollTo(0, Number.MAX_VALUE);',
                                  # wait_time=5,
                                  )

    def parse(self, response):

        scrap = True
        n_scrap = 300
        i = 0

        while scrap:

            i += 1
            game_link = response.xpath(
                f'/html/body/div[1]/div[4]/c-wiz/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/div[{i}]/c-wiz/div/div/div[2]/div/div/div[1]/div/div/div[1]/a/@href').get()

            if (game_link is None) and (i >= n_scrap):
                scrap = False

            if game_link is not None:
                game_url = 'http://play.google.com' + game_link

                yield SeleniumRequest(url=game_url,
                                      callback=self.parse_game,
                                      # https://stackoverflow.com/a/12792245
                                      script='window.scrollTo(0, Number.MAX_VALUE);',
                                      # wait_time=1,
                                      )

    def parse_game(self, response):

        # https://stackoverflow.com/a/48990753
        name = response.selector.xpath(
            '//c-wiz[1]/h1/span/text()').get()

        genre = response.xpath(
            '//div[1]/div/div[1]/div[1]/span[2]/a/text()').get()

        score = response.xpath(
            '//main/div/div[1]/c-wiz/div[1]/div[1]/text()').get()

        score_num = response.xpath(
            '//main/div/div[1]/c-wiz/div[1]/span/span[2]/text()').get()

        downloads = response.xpath(
            '//c-wiz[3]/div[1]/div[2]/div/div[3]/span/div/span/text()').get()

        description = response.xpath(
            '//c-wiz[3]/div/div[1]/div[2]/div[1]/span/div/text()').get()

        yield {
            'name': name,
            'genre': genre,
            'score': score,
            'score_num': score_num,
            'downloads': downloads,
            'description': description,
        }
