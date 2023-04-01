import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
import string


def check_company(customer):
    """
        A cégjegyzékszám alapján megnyitja a cégkivonatot, majd miután a felhasználó túljut a
        recaptcha ellenőrzésen, lementi az adatokat a cégről és elkészíti
        a szöveget az összehasonlításhoz
    """
    # Ha egyéni vállakozó, másik adatbázist használ
    if customer.registration_number == "@":
        return check_freelancer(customer)

    # Cégkivonat megnyitása
    reg_number = "".join(filter(lambda x: x in string.digits, customer.registration_number))
    driver = webdriver.Chrome()
    driver.get(f'https://www.e-cegjegyzek.hu/?cegadatlap/{reg_number}/TaroltCegkivonat')

    # Várakozás, amig a felhasználó megoldja a chapchát, de legfeljebb 300 másodpercig
    try:
        wait = WebDriverWait(driver, 300)
        new_tax_number = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "adoszam")))
        wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "adoszam"), new_tax_number.text))
    except TimeoutException:
        return "Nincs találat az adatbázisban, vagy nem jutottál át a recaptcha ellenőrzésen", None

    # elmentjük az új adatokat egy tömbbe és lérehozzuk a stringet
    update_customer = [driver.find_element(By.CLASS_NAME, "nev").text,
                       driver.find_element(By.CLASS_NAME, "szekhely").text,
                       driver.find_element(By.CLASS_NAME, "cjsz").text,
                       driver.find_element(By.CLASS_NAME, "adoszam").text]
    update_info = f"Szeretnék végrehajtani az alábbi módosításokat?\n" \
                  f"Régi név: {customer.company_name}\nÚj név: {update_customer[0]}\n\n" \
                  f"Régi cím: {customer.address}\nÚj cím: {update_customer[1]}\n\n" \
                  f"Régi adószám: {customer.tax_number}\nÚj adószám: {update_customer[3]}\n\n"

    # Teszt fázis
    # A felhasználó további 180 másodpercig használhatja  a böngészőt, majd utána bezárjuk
    try:
        WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.NAME, 'muhahahaha')))
    except TimeoutException:
        pass
    except NoSuchWindowException:
        pass
    # teszt fázis vége

    return update_info, update_customer


def check_freelancer(customer):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://www.nyilvantarto.hu/evny-lekerdezo/')

    tax_number = driver.find_element(By.NAME, "adoszam")
    tax_number.send_keys(customer.tax_number)
    # search button
    driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/form/button').click()

    time.sleep(2)
    # név, székhely, cégjegyzékszám, adószám
    name = driver.find_element(By.XPATH, '/html/body/div[5]/div[7]/div/span').text
    update_customer = [f"{name.title()} EV",
                       driver.find_element(By.XPATH, '/html/body/div[5]/div[9]/div[2]/div').text[14:].title(),
                       "@",
                       driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div[2]/span').text]
    update_info = f"Szeretnék végrehajtani az alábbi módosításokat?\n" \
                  f"Régi név: {customer.company_name}\nÚj név: {update_customer[0]}\n\n" \
                  f"Régi cím: {customer.address}\nÚj cím: {update_customer[1]}\n\n"

    is_on = driver.find_element(By.XPATH, '/html/body/div[5]/div[5]/div[1]/span').text
    if is_on != "Működő":
        return "Az adatbázis alapján az egyéni vállalkozó jelenleg inaktív", None
    print(name)

    return update_info, update_customer
