import os
import shutil
from shutil import which
from platform import system

from time import sleep
from datetime import datetime
from psutil import net_io_counters

import scrapy
from scrapy.selector import Selector

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
f_options = Options()


def load_main(url):

    try:
        start = datetime.now()

        send, recv = initialise()

        # set up the browser
        browser = setup()

        browser.get(url)
        print('loading...')
        print()

        # You can set your own pause time. My laptop is a bit slow so I use 1 sec
        scroll_pause_time = 1
        screen_height = browser.execute_script(
            "return window.screen.height;")   # get the screen height of the web
        i = 1

        while True:
            # scroll one screen height each time
            browser.execute_script(
                "window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
            i += 1
            sleep(scroll_pause_time)
            # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
            scroll_height = browser.execute_script(
                "return document.body.scrollHeight;")
            # Break the loop when the height we need to scroll to is larger than the total scroll height
            if (screen_height) * i > scroll_height:
                break

        sleep(1)

        source = browser.page_source

    except Exception as e:
        print(e)

    finally:

        net_update(send, recv)
        stop = datetime.now()
        dur_sec = getDuration(start, stop, 'seconds')

        print(dur_sec)
        print()
        print('All done!')
        print(
            '============================================================')
        print()
        # # delete_all_cookies and quit
        # browser.delete_all_cookies()
        browser.quit()

        return source


def setup():
    """sets up the browser"""

    print('setting up the browser!')
    then_set = datetime.now()

    f_options.add_argument("--headless")  # no GUI
    f_options.add_argument('--no-sandbox')
    f_options.add_argument("--ignore-certificate-error")
    f_options.add_argument("--ignore-ssl-errors")
    f_options.add_argument('window-size=1920x1080')
    browser = webdriver.Firefox(
        options=f_options, executable_path=which('geckodriver'))

    # browser.minimize_window()
    print('setup up complete!')
    now_set = datetime.now()
    print(getDuration(then_set, now_set, 'ms'))

    return browser


def initialise():
    """initialise the required variables"""

    send = net_io_counters().bytes_sent/1024./1024.  # convert_to_mbyte
    recv = net_io_counters().bytes_recv/1024./1024.  # convert_to_mbyte

    return send, recv


def net_update(old_send, old_recv):
    """bandwidth monitoring function"""

    new_send = net_io_counters().bytes_sent/1024./1024.  # convert_to_mbyte
    new_recv = net_io_counters().bytes_recv/1024./1024.  # convert_to_mbyte

    del_send = new_send - old_send
    del_recv = new_recv - old_recv

    print(f"send: {del_send:0.3f}")
    print(f"recieve: {del_recv:0.3f}")
    print()

    old_send = new_send
    old_recv = new_recv

    return new_send, new_recv, del_send, del_recv


def getDuration(then, now=datetime.now(), interval="default"):
    """
        Returns a duration as specified by variable interval
        Functions, except totalDuration, returns [quotient, remainder]

        Example usage:
            from datetime import datetime
            then = datetime(2012, 3, 5, 23, 8, 15)
            now = datetime.now()
            print(getDuration(then))
            >>> Time between dates: 7 years, 208 days, 21 hours, 19 minutes and 15 seconds
            print(getDuration(then, now, 'years'))   # years
            print(getDuration(then, now, 'days'))    # days
            print(getDuration(then, now, 'hours'))   # hours
            print(getDuration(then, now, 'minutes')) # minutes
            print(getDuration(then, now, 'seconds')) # seconds
            then = datetime.now()
            sleep(1)
            now = datetime.now()
            print(getDuration(then, now, 'hms'))
            >>> duration: 0 hours, 0 minutes and 1 seconds

        .. _ time difference between two datetime objects?
            https://stackoverflow.com/a/47207182
    """

    duration = now - then  # For build-in functions
    duration_in_s = duration.total_seconds()

    def years():
        return divmod(duration_in_s, 31536000)  # Seconds in a year=31536000.

    def days(seconds=None):
        # Seconds in a day = 86400
        return divmod(seconds if seconds != None else duration_in_s, 86400)

    def hours(seconds=None):
        # Seconds in an hour = 3600
        return divmod(seconds if seconds != None else duration_in_s, 3600)

    def minutes(seconds=None):
        # Seconds in a minute = 60
        return divmod(seconds if seconds != None else duration_in_s, 60)

    def seconds(seconds=None):
        if seconds != None:
            return divmod(seconds, 1)
        return duration_in_s

    def totalDuration():
        y = years()
        d = days(y[1])  # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])
        return f"Time between dates: {int(y[0])} years, {int(d[0])} days, {int(h[0])} hours, {int(m[0])} minutes and {int(s[0])} seconds"

    def hms():
        y = years()
        d = days(y[1])  # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])
        return f"duration: {int(h[0])} hours, {int(m[0])} minutes and {int(s[0])} seconds"

    def ms():
        y = years()
        d = days(y[1])  # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])
        return f"duration: {int(m[0])} minutes and {int(s[0])} seconds"

    return {
        'years': int(years()[0]),
        'days': int(days()[0]),
        'hours': int(hours()[0]),
        'minutes': int(minutes()[0]),
        'seconds': int(seconds()),
        'default': totalDuration(),
        'hms': hms(),
        'ms': ms(),
    }[interval]


class GamesSpider(scrapy.Spider):

    name = "games"

    def start_requests(self):
        urls = [
            'https://play.google.com/store/apps/collection/cluster?clp=0g4YChYKEHRvcGdyb3NzaW5nX0dBTUUQBxgD:S:ANO1ljLhYwQ&gsr=ChvSDhgKFgoQdG9wZ3Jvc3NpbmdfR0FNRRAHGAM%3D:S:ANO1ljIKta8',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main)

    def parse_main(self, response):

        scrap = True
        n_scrap = 300
        j = 0

        text = load_main(response.url)
        sel = Selector(text=text)

        while scrap:

            j += 1

            if j <= 50:
                string = f'//div[{j}]/c-wiz/div/div/div[2]/div/div/div[1]/div/div/div[1]/a/@href'
            else:
                string = f'//c-wiz[{j - 50}]/div/div/div[2]/div/div/div[1]/div/div/div[1]/a/@href'

            game_link = sel.xpath(string).get()

            if (j >= n_scrap):
                scrap = False

            if game_link is not None:
                game_url = 'http://play.google.com' + game_link

                yield scrapy.Request(url=game_url, callback=self.parse_game)

    def parse_game(self, response):

        #text = load_game(response.url)
        #sel = Selector(text=text)

        # https://stackoverflow.com/a/48990753
        name = response.xpath(
            '//c-wiz[1]/h1/span/text()').get()

        genre = response.xpath(
            '//div[1]/div/div[1]/div[1]/span[2]/a/text()').get()

        score = response.xpath(
            '//div[1]/div[1]/text()').get()

        score_num = response.xpath(
            '//div[1]/span/span[2]/text()').get()

        downloads = response.xpath(
            '//div/div[3]/span/div/span/text()').get()

        description = response.xpath(
            "//meta[@name='description']/@content")[0].extract()

        yield {
            'name': name,
            'genre': genre,
            'score': score,
            'score_num': score_num,
            'downloads': downloads,
            'description': description,
        }
