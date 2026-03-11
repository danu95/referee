#!/usr/bin/env python3

# neuer versuch!
# https://github.com/seleniumbase/SeleniumBase/tree/master/examples/cdp_mode
# from seleniumbase import SB
#
# with SB(uc=True, test=True, guest=True) as sb:
#     url = "www.planetminecraft.com/account/sign_in/"
#     sb.activate_cdp_mode(url)
#     sb.sleep(2)
#     sb.solve_captcha()
#     sb.wait_for_element_absent("input[disabled]")
#     sb.sleep(2)

# === Must have ===
# das ding muss wieder laufen

# === Nice to have ===
# chronjob, damit es regelmässig läuft?
# mail?

# === Import packages ===

from email import charset
from bs4 import BeautifulSoup
import os
import sys
import time
import re
import difflib
import smtplib
# import undetected_chromedriver as undetected
# from email.message import EmailMessage
# # from selenium import webdriver
# # from webdriver_manager.firefox import GeckoDriverManager
# # from selenium.webdriver.firefox.service import Service
# # from selenium.webdriver.firefox.options import Options
# from selenium.webdriver import Keys, ActionChains
# from selenium.webdriver.common.by import By 
# from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
# from selenium.webdriver.common.actions.action_builder import ActionBuilder
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as ECondition

from seleniumbase import SB

with SB(uc=True, test=True, guest=True) as sb:
    url = "https://www.clubcorner.ch/users/sign_in"
    print("websetie geöffnet")
    sb.activate_cdp_mode(url)
    sb.sleep(2)
    sb.solve_captcha()
    print("solve captcha")
    sb.wait_for_element_absent("input[disabled]")
    sb.sleep(2)
    print("done")
    sb.save_screenshot("debug_page.png")
    

# === Main ===
def main():
    url: str = "https://www.clubcorner.ch/users/sign_in"
    # csvFile: str = "changes.csv"
    old_file: str= 'old_soup.txt'
    new_file: str = 'new_soup.txt'
    start_w: str = 'Zukünftige Einsätze'
    end_w: str = 'Zukünftige Ausbildungen'

    # open_or_create_csv_file(csvFile)
    driver_setup(url)
    # scroll_down_press_forward()
    find_insert_login()
    time.sleep(2)
    press_anmelden()
    time.sleep(2)
    soup = get_page_source_and_create_soup()
    write_in_txt_file(soup, "new_soup.txt")
    time.sleep(2)

    # Get the cleaned data
    inhalt_old = extract_and_clean(old_file, start_w, end_w)
    inhalt_new = extract_and_clean(new_file, start_w, end_w)

    # Run the comparison
    unterschied: str | None = compare_sections(inhalt_old, inhalt_new, old_file, new_file)

    if inhalt_new != inhalt_old:
        print(unterschied)
        # Only send if there is actual text to send
        if unterschied:
            send_mail("Clubcorner Aufgebot", unterschied)
    else:
        print("No changes found, skipping email.")


    write_in_txt_file(soup, "old_soup.txt")
    time.sleep(2)
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
    # close_csv_file()
    driver_quit()

# === Driver setup & start ===
def driver_setup(url: str):
    global driver
    options = undetected.ChromeOptions()
    driver = undetected.Chrome(version_main=145, options=options)
    _ = driver.maximize_window()
    _ = driver.implicitly_wait(2)
    _ = driver.get(url)
    _ = driver.implicitly_wait(3)
    _ = time.sleep(5)

# === Driver Quit ===
def driver_quit():
    driver.quit()

# def open_or_create_csv_file(csvFile):
#     global datei
#     dir_list = os.listdir()
#     if (csvFile in dir_list):
#         try:
#             datei = open(csvFile,"w")
#         except:
#             print("Dateizugriff nicht erfolgreich")
#             sys.exit(0)
#     else:
#         with open(csvFile, 'w') as datei:
#             pass
#     return datei

def write_in_txt_file(soup: BeautifulSoup, filename: str) -> None:
    for i in soup:
        with open(filename, "w") as file:
            _ = file.write(soup.prettify())

# def write_in_csv_file(infos):
#     for i in infos:
#         datei.write(i + ',')
#     datei.write('\n')
#
# def close_csv_file():
#     datei.close

# def scroll_down_press_forward():
#     mouse = ActionChains(driver)
#     start_point = ScrollOrigin.from_viewport(0,0)
#     for i in range(5):
#         for j in range(15):
#             ActionChains(driver).scroll_from_origin(start_point, 0, 500).perform()
#             time.sleep(1)
#         try:
#             show_more = driver.find_element(By.PARTIAL_LINK_TEXT, "Mehr anzeigen")
#             mouse.move_to_element(show_more).click().perform()
#             time.sleep(1)
#         except:
#             print('1')

def get_page_source_and_create_soup():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup


def find_insert_login():
    # first we need to get some credentials
    mail_cc_from_txt: str
    pw_cc_from_txt: str
    mail_cc_from_txt, pw_cc_from_txt, _, _, _, = get_credentials()


    # now we search the mail element 
    email_field = driver.find_element(By.ID, "user_email")
    # Type directly into the element
    _ = email_field.send_keys(mail_cc_from_txt)
    # Now check the value
    values_are: str | None = email_field.get_attribute('value')
    assert values_are == mail_cc_from_txt

    time.sleep(2)

    # now we search the mail element 
    pw_field = driver.find_element(By.ID, "user_password")
    # Type directly into the element
    _ = pw_field.send_keys(pw_cc_from_txt)
    # Now check the value
    values_are: str | None = pw_field.get_attribute('value')
    assert values_are == pw_cc_from_txt

    time.sleep(2)

def get_credentials():
    with open("pw.txt") as f:
        mail_cc_from_txt: str = f.readline().strip()
        pw_cc_from_txt: str = f.readline().strip()
        from_mail_txt: str = f.readline().strip()
        to_mail_txt: str = f.readline().strip()
        pw_from_mail_txt: str = f.readline().strip()
    return mail_cc_from_txt, pw_cc_from_txt, from_mail_txt, to_mail_txt, pw_from_mail_txt


def press_anmelden():
    mouse = ActionChains(driver)
    anmelden_button = driver.find_element(By.ID, "devise-session-submit")
    mouse.move_to_element(anmelden_button).click().perform()


def extract_and_clean(filename: str, start_word: str, end_word: str):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        
    start_idx = content.find(start_word)
    end_idx = content.find(end_word)

    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        # Extract the section
        section = content[start_idx : end_idx + len(end_word)]
        
        # Cleaning: Split into lines, strip whitespace, and remove empty lines
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        return lines
    
    return None


def compare_sections(old_inhalt: list[str] | None, new_inhalt: list[str] | None, file_old: str, file_new: str):
    # The truthiness check ensures both extractions were successful
    if old_inhalt is not None and new_inhalt is not None:
        if file_old == file_new:
            print(f"The sections in '{file_old}' and '{file_new}' are identical.")
            return None
        else:
            print(f"Changes found between markers in '{file_old}' vs '{file_new}':\n")
            
            # Generating the diff output
            diff = difflib.unified_diff(
                old_inhalt, 
                new_inhalt, 
                fromfile=file_old, 
                tofile=file_new,
                lineterm=''
            )

            diff_list = list(diff)

            # This 'attribute' joins all diff lines into one big string
            diff_output = '\n'.join(list(diff_list))
            return diff_output
    else:
        print("Error: Markers ('Zukünftige...') not found or in wrong order in one or both files.")


def send_mail(subject_mail: str, message_mail: str):
    _, _, from_mail_txt, to_mail_txt, pw_from_mail_txt = get_credentials()

    msg = EmailMessage()
    msg['Subject'] = subject_mail
    msg['From'] = from_mail_txt
    msg['To'] = to_mail_txt
    
    msg.set_content(message_mail)

    # Add the html version.  This converts the message into a multipart/alternative
    # container, with the original text message as the first part and the new html
    # message as the second part.

    msg.add_alternative(f"""\
    <html>
      <head></head>
      <body>
            <h3>Neue Änderungen gefunden:</h3>
            <pre style="font-family: monospace; background-color: #f4f4f4; padding: 10px;">
            {message_mail}
            </pre>
      </body>
    </html>
    """, subtype='html')
    # note that we needed to peel the <> off the msgid for use in the html.

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        _ = server.starttls()
        _ = server.login(from_mail_txt, pw_from_mail_txt)

        _ = server.send_message(msg)
        print("email gesendet")












# def get_all_href_from_urls(soup):
#     all_urls = [a['href'] for a in soup('a') if a.has_attr('href')]
#     return all_urls

# def filter_relevant_href(all_urls):
#     myFilter = r"^https://www.sfl.ch/spieldetail/detail/"
#     relevant_urls = [url for url in all_urls if re.match(myFilter, url)]
#     relevant_urls = list(set(relevant_urls))
#     return relevant_urls

# get the actual referees from the page
# def find_all_infos(soup):
#     try:
#         ref_tag = soup.find('strong', string="SCHIEDSRICHTER")
#         ref1 = ref_tag.next_sibling.next_sibling
#         ref2 = ref1.next_sibling.next_sibling
#         ref3 = ref2.next_sibling.next_sibling
#         ref4 = ref3.next_sibling.next_sibling
#         datum = soup.find('div', class_="c-matchdetail-hero__date u-text-semibold u-text-center").next.next.next
#         datum = (''.join(datum.splitlines())).lstrip()
#         runde = soup.find('div', class_="c-matchdetail-hero__round u-text-center u-text-semibold").next
#         home = soup.find('p', class_="u-visible-md-up").next
#         away = home.find_next('p', class_="u-visible-md-up").next
#         spielinfos = [runde, datum, home, away, ref1, ref2, ref3, ref4]
#         return spielinfos
#     except:
#         pass
    


    
# main()



