import os
import time
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Configuración de Logs y Carpetas
os.makedirs("reports/screenshots", exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.default_timeout = 15  # Aumentado a 15s para evitar Timeouts
        self.wait = WebDriverWait(driver, self.default_timeout)
        self.logger = logging.getLogger(self.__class__.__name__)

    def open_url(self, url: str):
        self.logger.info(f"Navegando a: {url}")
        self.driver.get(url)
        time.sleep(3)  # Espera técnica para carga de recursos de Strapi

    def find_element(self, locator: tuple):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator: tuple):
        """Intenta hacer click manejando intercepciones comunes en SPAs."""
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except ElementClickInterceptedException:
            self.logger.warning(f"Click interceptado en {locator}, reintentando con JS...")
            element = self.driver.find_element(*locator)
            self.driver.execute_script("arguments[0].click();", element)
        except TimeoutException:
            self.take_screenshot("ERROR_TIMEOUT_CLICK")
            raise

    def send_keys(self, locator: tuple, text: str):
        try:
            element = self.find_element(locator)
            element.click()
            element.clear()
            element.send_keys(text)
        except TimeoutException:
            self.take_screenshot("ERROR_TIMEOUT_SENDKEYS")
            raise

    def get_text(self, locator: tuple) -> str:
        try:
            return self.find_element(locator).text
        except TimeoutException:
            return ""

    def take_screenshot(self, name: str):
        """Toma captura con Timestamp para no sobrescribir evidencias."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"reports/screenshots/{timestamp}_{name}.png"
        self.driver.save_screenshot(filename)
        self.logger.info(f"📸 Captura guardada: {filename}")