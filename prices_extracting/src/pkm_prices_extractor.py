import pandas as pd
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GRADE_TO_ID = {
    "8": "new_price",
    "9": "graded_price",
    "10": "manual_only_price"
}


def find_grade_value(tab, grade):
    grade_element = WebDriverWait(tab, 10).until(
        EC.presence_of_element_located((By.ID, GRADE_TO_ID[grade]))
    )
    raw_value = grade_element.text
    if raw_value == "N/A":
        return "N/A"
    try:
        grade_value = int(round(float(raw_value.split(" ")[0].replace("$", "").replace(",", ""))))
    except ValueError:
        print("Error parsing grade value: ", raw_value)
        return "N/A"
    return grade_value


def get_card_prices(tab, card_link):
    tab.get(card_link)
    psa8_price = find_grade_value(tab, "8")
    psa9_price = find_grade_value(tab, "9")
    psa10_price = find_grade_value(tab, "10")
    return psa8_price, psa9_price, psa10_price


def fill_prices(csv_df, tab, psa8_list, psa9_list, psa10_list):
    for index, row in csv_df.iterrows():
        try:
            if row["Language"] != "English" or 'base set' in row["Set"].lower() or 'jungle' in row["Set"].lower():
                psa8_list.append(None)
                psa9_list.append(None)
                psa10_list.append(None)
                continue
            to_search = f"{row['Set']} #{row['Card Number']}"
            print("Finding price for card: ", row["Card Name"], to_search)
            search_box = WebDriverWait(tab, 10).until(
                EC.presence_of_element_located((By.ID, "game_search_box"))
            )
            search_box.send_keys(to_search)
            search_box.send_keys("\n")
            options = WebDriverWait(tab, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@data-product]"))
            )
            card_links = []
            for option in options:
                card_name_tr = option.find_element(By.CLASS_NAME, "title")
                card_name = card_name_tr.find_element(By.TAG_NAME, 'a').get_attribute('textContent')
                set_name_tr = option.find_element(By.CLASS_NAME, "console")
                set_name = set_name_tr.get_attribute('textContent')
                if "(" in card_name:
                    card_name = card_name.split("(")[0]
                card_link = card_name_tr.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print("card_name: ", card_name)
                if ('1st edition' not in card_name.lower()
                        and 'japanese' not in card_name.lower()
                        and 'prerelease' not in card_name.lower()
                        and 'pre-release' not in card_name.lower()
                        and 'pre release' not in card_name.lower()
                        and 'promo' not in card_name.lower()
                        and 'error' not in card_name.lower()
                        and 'japanese' not in set_name.lower()
                        and 'reverse holo' not in card_name.lower()
                        and row['Set'].lower() in set_name.lower()):
                    card_links.append(card_link)
            if len(card_links) == 0 or len(card_links) > 1:
                psa8_list.append(None)
                psa9_list.append(None)
                psa10_list.append(None)
                if len(card_links) > 1:
                    print("Multiple cards found for: ", to_search)
                    continue
                if len(card_links) == 0:
                    print("No cards found for: ", to_search)
                    continue
            psa8_price, psa9_price, psa10_price = get_card_prices(tab, card_links[0])
            psa8_list.append(psa8_price)
            psa9_list.append(psa9_price)
            psa10_list.append(psa10_price)
        except Exception as e:
            print(f"Error getting card prices for: {row['Card Name']} / {row['Set']} - {e}")
            psa8_list.append(None)
            psa9_list.append(None)
            psa10_list.append(None)
            continue


def init_browser_and_fill_csv(csv_file_path):
    browser = selenium.webdriver.Chrome()
    browser.implicitly_wait(10)
    browser.get("https://www.pricecharting.com/")
    csv_df = pd.read_csv(csv_file_path)
    psa8_list = []
    psa9_list = []
    psa10_list = []
    fill_prices(csv_df, browser, psa8_list, psa9_list, psa10_list)
    csv_df["psa8_price"] = psa8_list
    csv_df["psa9_price"] = psa9_list
    csv_df["psa10_price"] = psa10_list
    csv_df.to_csv("full_" + csv_file_path, index=False)
    browser.quit()


if __name__ == "__main__":
    init_browser_and_fill_csv("../assets/test_cards_table.csv")





# import selenium
#
#
# def fill_prices(csv_df, tab, psa8_list, psa9_list, psa10_list):
#     """Returns a list of prices for each card in the file"""
#     for row in csv_df.itterrows():
#         print("Finding price for card: ", row["name"])
#         to_search = row['set'] + " #" + row['number']
#         tab.find_element_by_id("search").send_keys(to_search)
#         tab.press_keys("\n")
#         options = tab.find_elements_by_attribute("data-product")
#         card_links = []
#         for option in options:
#             card_name_tr = option.find_element_by_class("title")
#             card_name = card_name_tr.children[0].value
#             card_link = card_name_tr.children[0].href
#             if '1st edition' not in lower(card_name):
#                 card_links.append(card_link)
#         if len(card_links) == 0 or len(card_links) > 1:
#             psa8_list.append(np.nan)
#             psa9_list.append(np.nan)
#             psa10_list.append(np.nan)
#         if len(card_links) > 1:
#             print("Multiple cards found for: ", row["name"])
#             continue
#         if len(card_links) == 0:
#             print("No cards found for: ", row["name"])
#             continue
#         psa8_price, psa9_price, psa10_price = get_card_prices(tab, card_links[0])
#         psa8_list.append(psa8_price)
#         psa9_list.append(psa9_price)
#         psa10_list.append(psa10_price)
#
#
# def get_card_prices(tab, card_link):
#     tab.get(card_link)
#     psa8_price = find_grade_value(tab, "8")
#     psa9_price = find_grade_value(tab, "9")
#     psa10_price = find_grade_value(tab, "10")
#     return psa8_price, psa9_price, psa10_price
#
#
# GRADE_TO_ID = {
#     "8": "new_price",
#     "9": "graded_price",
#     "10": "manual_only_price"
# }
#
#
# def find_grade_value(tab, grade):
#     grade_element = tab.find_element_by_id(GRADE_TO_ID[grade])
#     grade_value = math.round(grade_element.children[0].value)
#     return int(grade_value)
#
#
# def init_browser_and_fill_csv(csv_file_path):
#     """Returns a selenium webdriver.Chrome object"""
#     browser = selenium.webdriver.Chrome()
#     tab = browser.get("https://www.pricecharting.com/")
#     csv_df = pd.read_csv(csv_file_path)
#     psa8_list = []
#     psa9_list = []
#     psa10_list = []
#     fill_prices(csv_df, tab, psa8_list, psa9_list, psa10_list)
#     csv_df["psa8_price"] = psa8_list
#     csv_df["psa9_price"] = psa9_list
#     csv_df["psa10_price"] = psa10_list
#     csv_df.to_csv(csv_file_path, index=False)
