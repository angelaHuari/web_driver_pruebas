from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Selectores estables
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[name='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    
    # CORRECCIÓN AQUÍ:
    # 1. Usamos By.ID porque el elemento tiene id="global-form-error"
    # 2. Si prefieres XPath, sería "//span[contains(text(), 'Invalid')]" (span, no div)
    ERROR_MESSAGE = (By.ID, "global-form-error")

    def login(self, email, password):
        self.send_keys(self.EMAIL_INPUT, email)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.take_screenshot("1_formulario_login_lleno")
        self.click(self.SUBMIT_BTN)

    def get_error_message(self):
        # get_text ya debería incluir una espera explícita en tu BasePage
        return self.get_text(self.ERROR_MESSAGE)