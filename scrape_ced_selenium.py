from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import json
import time

def scrape_ced_with_selenium():
    print("=" * 70)
    print("🦊 Firefox ile EÇED'den İstanbul Ulaşım Projeleri Çekiliyor (Tüm Sayfalar)")
    print("=" * 70)

    options = webdriver.FirefoxOptions()
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    # options.add_argument("--headless")  # test için kapalı tut

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    driver.get("https://eced-duyuru.csb.gov.tr/eced-prod/duyurular.xhtml")

    try:
        wait = WebDriverWait(driver, 20)
        time.sleep(5)

        # İl: İstanbul
        il_input = wait.until(EC.presence_of_element_located((By.ID, "form:duyuru-arama-fieldset:j_idt26_input")))
        il_input.clear()
        il_input.send_keys("İSTANBUL")
        time.sleep(1)
        il_input.send_keys(Keys.ARROW_DOWN)
        il_input.send_keys(Keys.ENTER)

        # Sektör: Ulaşım
        sektor_input = wait.until(EC.presence_of_element_located((By.ID, "form:duyuru-arama-fieldset:j_idt28_input")))
        sektor_input.clear()
        sektor_input.send_keys("Ulaşım")
        time.sleep(1)
        sektor_input.send_keys(Keys.ARROW_DOWN)
        sektor_input.send_keys(Keys.ENTER)

        # Ara butonu
        ara_button = wait.until(EC.element_to_be_clickable((By.ID, "form:duyuru-arama-fieldset:j_idt44")))
        driver.execute_script("arguments[0].click();", ara_button)
        time.sleep(4)

        projeler = []
        sayfa = 1

        while True:
            print(f"📄 Sayfa {sayfa} çekiliyor...")
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody[id*='duyurTable_data'] > tr.ui-widget-content")

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 9:
                    continue
                projeler.append({
                    "il": cells[0].text.strip(),
                    "ilce": cells[1].text.strip(),
                    "proje_adi": cells[2].text.strip(),
                    "proje_sahibi": cells[3].text.strip(),
                    "sektor": cells[4].text.strip(),
                    "alt_sektor": cells[5].text.strip(),
                    "durum": cells[6].text.strip(),
                    "tarih": cells[7].text.strip(),
                    "proje_turu": cells[8].text.strip()
                })

            # Sonraki sayfa var mı?
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(@class,'ui-paginator-next') and not(contains(@class,'ui-state-disabled'))]")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
                sayfa += 1
            except:
                print("✅ Tüm sayfalar çekildi.")
                break

        print(f"📊 Toplam {len(projeler)} İstanbul ulaşım projesi bulundu")
        with open("ced_istanbul_ulasim.json", "w", encoding="utf-8") as f:
            json.dump(projeler, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ Selenium hatası: {e}")
        driver.save_screenshot("eced_debug_firefox.png")
        print("📸 Hata ekran görüntüsü: eced_debug_firefox.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_ced_with_selenium()