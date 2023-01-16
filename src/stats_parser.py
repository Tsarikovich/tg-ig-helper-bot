import random
import time

from exceptions import DataNotParsedException, ProxyConnectionException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from src import config
from src.config import SELENIUMWIRE_OPTIONS, USERAGENTS, logger


def create_chrome_options(user_agent):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.accept_insecure_certs = True
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--user-agent={user_agent}')
    chrome_options.add_argument('--no-sandbox')

    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    return chrome_options


class StatsParser:
    def __init__(self):
        self.driver = None
        self.limit_attempt = 30
        self.attempt = 0

    def parse(self, nickname):
        return self.try_get_response(self.get_hypeauditor_data)(nickname)

    def try_get_response(self, func):
        def wrapper(*args, **kwargs):
            try:

                return func(*args, **kwargs)

            except DataNotParsedException as e:
                logger.info(e)
                return {}

            except ProxyConnectionException as e:
                time.sleep(2)
                if (
                    'HTTPSConnectionPool' not in str(e)
                    and 'ERR_TUNNEL_CONNECTION_FAILED' not in str(e)
                    and 'Timed out receiving message' not in str(e)
                ):

                    self.attempt += 1

                    if self.attempt != self.limit_attempt:
                        return wrapper(*args, **kwargs)
                    else:
                        self.attempt = 0
                        return None
                else:
                    return wrapper(*args, **kwargs)

        return wrapper

    def safe_find_element(self, xpath, flag=False) -> WebElement:
        try:
            if flag:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )
            else:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

        except Exception as e:
            raise DataNotParsedException(f'Time limit exceeded: {e}')

        return self.driver.find_element(By.XPATH, xpath)

    def get_hypeauditor_data(self, entity):
        try:
            logger.info('Getting hypeauditor data')
            if self.driver is None:
                self.driver = self.init_driver(random.choice(USERAGENTS), True)

            self.driver.get(f'https://hypeauditor.com/instagram/{entity}')

            if '502 Bad Gateway' in self.driver.page_source:
                raise ProxyConnectionException('502')
            elif (
                self.driver.current_url
                == 'https://hypeauditor.com/reports/instagram/'
            ):
                return None

            return {
                'growth_4_weeks': self.safe_float(
                    self.safe_find_element(
                        '//*[@id="__layout"]/div/main/div[3]/div/div[2]/div[2]/div[1]/div[1]/div[2]'
                    )
                    .text.split(' ')[-1]
                    .replace('%', '')
                )
                / 100,
                'Avg. Engagement1': self.safe_float(
                    self.safe_find_element(
                        '//*[@id="__layout"]/div/main/div[2]/div[1]/div[1]/div[2]/div/div[2]'
                    )
                    .text.split('\n')[1]
                    .replace('%', '')
                )
                / 100,
                'Followers': self.safe_float(
                    self.safe_find_element(
                        '//*[@id="__layout"]/div/main/div[2]/div[1]/div[1]/div[2]/div/div[1]'
                    ).text.split('\n')[1]
                ),
            }

        except Exception as e:
            logger.debug(e)
            raise ProxyConnectionException(e)

    @staticmethod
    def init_driver(useragent, with_proxy=False):
        if with_proxy:

            driver = webdriver.Chrome(
                chrome_options=create_chrome_options(useragent),
                seleniumwire_options=SELENIUMWIRE_OPTIONS,
            )
        else:
            driver = webdriver.Chrome(
                chrome_options=create_chrome_options(useragent),
            )

        driver.set_page_load_timeout(20)
        driver.execute_cdp_cmd(
            'Page.addScriptToEvaluateOnNewDocument',
            {
                'source': """
                                  Object.defineProperty(navigator, 'webdriver', {
                                    get: () => undefined
                                  })
                                """
            },
        )

        return driver

    @staticmethod
    def safe_float(str_value=None):
        try:
            is_k = False
            is_m = False

            if isinstance(str_value, str):
                str_value = str_value.replace(',', '').replace(' ', '')
                if 'K' in str_value:
                    str_value = str_value.replace('K', '')
                    is_k = True
                if 'M' in str_value:
                    str_value = str_value.replace('M', '')
                    is_m = True

            if is_m:
                value = float(str_value) * 1000000
            elif is_k:
                value = float(str_value) * 1000
            else:
                value = float(str_value)

            return value
        except Exception as e:
            logger.debug(e)
            return -1


def parse():
    parser = StatsParser()

    result = {}

    with open(config.PathTo.SOURCE_TRAFFIC_GROUPS) as file:
        data = file.read().split('\n')
        for element in data:
            name = element.split(',')[0]
            print(f'Analyzing {name}')
            result_ = parser.parse(name)
            result[name] = result_
            print(result_)

        print(result)


if __name__ == '__main__':
    parse()
