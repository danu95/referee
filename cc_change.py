#!/usr/bin/env python3

# === Must have ===
# das ding muss wieder laufen

# === Nice to have ===
# chronjob, damit es regelmässig läuft?
# mail?

# === Import packages ===

from bs4 import BeautifulSoup
import os
import sys
import time
import re
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver import ActionChains


def main():
    url: str = "https://www.clubcorner.ch/users/sign_in"
    # csvFile: str = "changes.csv"
    
    # open_or_create_csv_file(csvFile)
    driver_setup(url)
    # scroll_down_press_forward()
    soup = get_page_source_and_create_soup()
    print(soup) 
    write_in_txt_file(soup, "soup.txt")
    # write_in_csv_file(soup)
    # all_urls = get_all_href_from_urls(soup)
    # relevant_urls = filter_relevant_href(all_urls)
    # for i in range(len(relevant_urls)):
    #     driver.get(relevant_urls[i])
    #     soup = get_page_source_and_create_soup()
    #     infos = find_all_infos(soup)
    #     try:
    #         write_in_csv_file(infos)
    #     except:
    #         pass
    # driver_quit()
    #
    # visible_break = ['Hier könnte ihre Werbung stehen']
    # #visible_break = ['-', '-', '-', '-', '-', '-', '-', '-']
    # for i in range (3): 
    #     write_in_csv_file(visible_break)
    #
    # url = "https://www.sfl.ch/resultate/"
    # driver_setup(url)
    # scroll_down_press_forward()
    # soup = get_page_source_and_create_soup()
    # all_urls = get_all_href_from_urls(soup)
    # relevant_urls = filter_relevant_href(all_urls)
    # for i in range(len(relevant_urls)):
    #     driver.get(relevant_urls[i])
    #     soup = get_page_source_and_create_soup()
    #     infos = find_all_infos(soup)
    #     try:
    #         write_in_csv_file(infos)
    #     except:
    #         pass

    # close_csv_file()
    driver_quit()





def driver_setup(url: str):
    global driver
    # service = Service('/path/to/firefoxdriver')
    # driver = webdriver.Firefox(service=service)
    options = Options()
    profile_path = "/home/daniel/.mozilla/firefox/40668zc4.default-esr"
    options.add_argument("-profile")
    options.add_argument(profile_path)

    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    driver.maximize_window()
    driver.implicitly_wait(2)
    _ = driver.get(url)
    driver.implicitly_wait(3)
    time.sleep(5)

def driver_quit():
    driver.quit()

def open_or_create_csv_file(csvFile):
    global datei
    dir_list = os.listdir()
    if (csvFile in dir_list):
        try:
            datei = open(csvFile,"w")
        except:
            print("Dateizugriff nicht erfolgreich")
            sys.exit(0)
    else:
        with open(csvFile, 'w') as datei:
            pass
    return datei

def write_in_txt_file(soup: BeautifulSoup, filename: str) -> None:
    for i in soup:
        with open(filename, "w") as file:
            _ = file.write(soup.prettify())

def write_in_csv_file(infos):
    for i in infos:
        datei.write(i + ',')
    datei.write('\n')

def close_csv_file():
    datei.close

def scroll_down_press_forward():
    mouse = ActionChains(driver)
    start_point = ScrollOrigin.from_viewport(0,0)
    for i in range(5):
        for j in range(15):
            ActionChains(driver).scroll_from_origin(start_point, 0, 500).perform()
            time.sleep(1)
        try:
            show_more = driver.find_element(By.PARTIAL_LINK_TEXT, "Mehr anzeigen")
            mouse.move_to_element(show_more).click().perform()
            time.sleep(1)
        except:
            print('1')

def get_page_source_and_create_soup():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

def get_all_href_from_urls(soup):
    all_urls = [a['href'] for a in soup('a') if a.has_attr('href')]
    return all_urls

def filter_relevant_href(all_urls):
    myFilter = r"^https://www.sfl.ch/spieldetail/detail/"
    relevant_urls = [url for url in all_urls if re.match(myFilter, url)]
    relevant_urls = list(set(relevant_urls))
    return relevant_urls

# get the actual referees from the page
def find_all_infos(soup):
    try:
        ref_tag = soup.find('strong', string="SCHIEDSRICHTER")
        ref1 = ref_tag.next_sibling.next_sibling
        ref2 = ref1.next_sibling.next_sibling
        ref3 = ref2.next_sibling.next_sibling
        ref4 = ref3.next_sibling.next_sibling
        datum = soup.find('div', class_="c-matchdetail-hero__date u-text-semibold u-text-center").next.next.next
        datum = (''.join(datum.splitlines())).lstrip()
        runde = soup.find('div', class_="c-matchdetail-hero__round u-text-center u-text-semibold").next
        home = soup.find('p', class_="u-visible-md-up").next
        away = home.find_next('p', class_="u-visible-md-up").next
        spielinfos = [runde, datum, home, away, ref1, ref2, ref3, ref4]
        return spielinfos
    except:
        pass
    


    
main()



