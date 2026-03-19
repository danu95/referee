#!/usr/bin/env python3

# Das Script läuft als cronjob (zum sehen welche jobs laufen 'crontab -l').

# === Done ===
# das ding muss wieder laufen
# chronjob, damit es regelmässig läuft
# mail

# === Import packages ===

from email import charset
from bs4 import BeautifulSoup
import os, time, datetime, getpass
import sys
import re
import difflib
import smtplib
# import undetected_chromedriver as undetected
from email.message import EmailMessage
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
from seleniumbase import Driver

    

# === Main ===
def main():

    now = datetime.datetime.now()
    user = getpass.getuser()
    file = os.path.basename(__file__) if "__file__" in globals() else "terminal"
    print(f"[{now}] [{user}@{file}] Let's start!")

    url: str = "https://www.clubcorner.ch/users/sign_in"
    # csvFile: str = "changes.csv"
    old_file: str= 'old_soup.txt'
    new_file: str = 'new_soup.txt'
    start_w: str = 'mit eigener Beteiligung'
    end_w: str = 'ohne eigene Beteiligung'

    global driver
    with SB(uc=True, test=True, guest=True, window_size='1920,1080') as driver:
        url = "https://www.clubcorner.ch/users/sign_in"
        driver.activate_cdp_mode(url)
        driver.sleep(2)
        driver.solve_captcha()
        driver.wait_for_element_absent("input[disabled]")
        driver.sleep(2)
        # driver.save_screenshot("debug_page.png")

        # open_or_create_csv_file(csvFile)
        # driver_setup(url)
        # scroll_down_press_forward()
        find_insert_login()
        time.sleep(1)
        press_anmelden()
        print("login ok")
        driver.save_screenshot("login_ok.png")
        time.sleep(1)

        select_SR()
        driver.save_screenshot("final_page.png")


        soup = get_page_source_and_create_soup()
        write_in_txt_file(soup, "new_soup.txt")
        time.sleep(1)

        # Get the cleaned data
        inhalt_old = extract_and_clean(old_file, start_w, end_w)
        inhalt_new = extract_and_clean(new_file, start_w, end_w)

        # Run the comparison
        unterschied: str | None = compare_sections(inhalt_old, inhalt_new, old_file, new_file)

        if inhalt_new != inhalt_old:
            print(unterschied)
            # Only send if there is actual text to send
            if unterschied:
                send_mail("Coaching Bericht", unterschied)
        else:
            print("No changes found, skipping email.")


        write_in_txt_file(soup, "old_soup.txt")
        time.sleep(2)
        print("finale")


# === Driver Quit ===
def driver_quit():
    driver.__quit_all_drivers()


def write_in_txt_file(soup: BeautifulSoup, filename: str) -> None:
    for i in soup:
        with open(filename, "w") as file:
            _ = file.write(soup.prettify())


def get_page_source_and_create_soup():
    page_source = driver.get_page_source()
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup


def find_insert_login():
    # first we need to get some credentials
    mail_cc_from_txt: str
    pw_cc_from_txt: str
    mail_cc_from_txt, pw_cc_from_txt, _, _, _, = get_credentials()

    _ = driver.wait_for_element("#user_email", timeout=10)
    
    # 1. Type into the field (handles the 'find' and the 'wait' automatically)
    driver.type("#user_email", mail_cc_from_txt)
    # 2. Assert the value (built-in retry logic if the UI is slow)
    driver.assert_text(mail_cc_from_txt, "#user_email")


    time.sleep(1)

    # --- Password Field ---
    # SeleniumBase finds By.ID automatically if you use the '#' prefix
    driver.type("#user_password", pw_cc_from_txt)
    driver.assert_text(pw_cc_from_txt, "#user_password")


    time.sleep(1)

    # driver.save_screenshot("credentials_written.png")

def get_credentials():
    with open("pw.txt") as f:
        mail_cc_from_txt: str = f.readline().strip()
        pw_cc_from_txt: str = f.readline().strip()
        from_mail_txt: str = f.readline().strip()
        to_mail_txt: str = f.readline().strip()
        pw_from_mail_txt: str = f.readline().strip()
    return mail_cc_from_txt, pw_cc_from_txt, from_mail_txt, to_mail_txt, pw_from_mail_txt


def press_anmelden():
    # This automatically moves the mouse to the element and clicks it
    driver.click("#devise-session-submit")
    time.sleep(5)

# driver.save_screenshot("main_page.png")
# def press_anmelden():
#     mouse = ActionChains(driver)
#     anmelden_button = driver.find_element(By.ID, "devise-session-submit")
#     mouse.move_to_element(anmelden_button).click().perform()

def select_SR():
    # 1. Click the dropdown toggle to open the menu
    # The ID 'kontextmenue_aufklappen' is unique, so we use that.
    driver.click("#kontextmenue_aufklappen")

    
    # 2. Click the "Schiedsrichter / Coach" link
    # We use a partial link text selector or a CSS selector for the href.
    # The href "/schiedsrichter/belegungsplan" is the safest unique identifier here.
    driver.click('a[href="/schiedsrichter/belegungsplan"]')
    time.sleep(5)
    # driver.window_size(1920,1080)
    
    # This clicks the link that goes to inspection results
    # It corresponds to 'SR Coaching Ergebnisse' in your HTML
    driver.wait_for_element_clickable('a[href="/schiedsrichter/inspektionsergebnisse"]')
    driver.wait_for_element_present('a[href="/schiedsrichter/inspektionsergebnisse"]')
    driver.click('a[href="/schiedsrichter/inspektionsergebnisse"]')
    
    
    time.sleep(5)

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
        print("Error: Markers ('...Beteiligung...') not found or in wrong order in one or both files.")


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



    
main()



