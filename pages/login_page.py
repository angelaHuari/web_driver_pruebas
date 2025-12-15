from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    
    # Selectores
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[name='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    # Selector que busca texto de error genérico o ID de error
    ERROR_MESSAGE = (By.XPATH, "//*[contains(text(), 'Invalid credentials') or contains(@id, 'error')]")

    def login(self, email, password):
        self.logger.info(f"Login con: {email}")
        self.send_keys(self.EMAIL_INPUT, email)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BTN)

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)