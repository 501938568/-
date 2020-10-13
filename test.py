from selenium import webdriver
import pickle
from time import sleep


def get_bili_cookies():
    try:
        open('biliCookies.pickle')
    except FileNotFoundError:
        browser = webdriver.Firefox(executable_path="D:\GeckoDriver\geckodriver")
        browser.get("https://passport.bilibili.com/login")
        while True:
            sleep(3)
            while browser.current_url == "https://www.bilibili.com/":
                bili_cookies = browser.get_cookies()
                browser.quit()
                cookies = {}
                for item in bili_cookies:
                    cookies[item['name']] = item['value']
                with open('biliCookies.pickle', 'wb') as new_pickle:
                    pickle.dump(cookies, new_pickle)

                return cookies['SESSDATA'], cookies['bili_jct']
    else:
        with open('biliCookies.pickle', 'rb') as file:
            data = pickle.load(file)
        return data['SESSDATA'], data['bili_jct']



if __name__ == '__main__':
    a = get_bili_cookies()
    pass