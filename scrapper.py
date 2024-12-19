import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=service,options=options)
driver.get('https://www.kultur.bamberg.de/_plaza/kuba.cfm?fts=&fid=Alle&f=Kategorien.KategorieID&lst=1')
#driver.get('https://www.kultur.bamberg.de/_plaza/kuba.cfm?lk&xstart=1&xwv=alle&sort=Veranstaltungen.Startzeit,Veranstaltungen.Veranstaltung&f=Kategorien.KategorieID&fid=Alle&ft=&fts=&st=-1&sm=&sj=&et=-1&em=&ej=&start=1&wv=22&lst=1&sk=0&ww=0&rub=0&ak=0&th=0&tid=0&vr=0&jt=0&akt=0')
wait = WebDriverWait(driver, 10)
print("ChromeDriver is working!")

def closeOverlay(driver):
    try:
        overlay = driver.find_element(By.CLASS_NAME, "termsfeed-com---nb-interstitial-overlay")
        driver.execute_script("arguments[0].style.display = 'none';", overlay)
        print("Overlay closed successfully.")
    except Exception:
        print("No overlay found or already removed.")

def getEventDescription(link,driver):
    try:
        closeOverlay(driver)
        print(f"Getting description for: {link}")
        driver.get(link)
        description = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-md-12 > p"))).text.strip()
        driver.back()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table"))) 
        return description
    except Exception as e:
        print(f"Error getting event description: {e}")
        driver.back()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table"))) 
        return "Description not available"
    
def scrapeTable(driver):
    events = []
    try:
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table")))
        rows = table.find_elements(By.XPATH, ".//tr[position() > 1]")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                eventNameLink = cells[2].find_element(By.TAG_NAME, "a").get_attribute("href")
                event = {
                    "Date & Time": cells[0].text.strip(),
                    "Category": cells[1].text.strip(),
                    "Event Name": cells[2].text.strip(),
                    "Location": cells[3].text.strip()
                }
                event ["Description"] = getEventDescription(eventNameLink,driver)
                events.append(event)
    except Exception as e:
        print(f"Error scraping table: {e}")
    return events
allEvents =[]
closeOverlay(driver)
allEvents=scrapeTable(driver)
with open("eventsTable.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Date & Time", "Category", "Event Name", "Location","Description"])
    writer.writeheader()
    writer.writerows(allEvents)
driver.quit()


