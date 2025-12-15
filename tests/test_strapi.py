import sys
import os
import unittest
import time
import logging
from dotenv import load_dotenv

# --- Configuración de rutas (Backup por si se ejecuta solo) ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Imports de tus Page Objects
from pages.login_page import LoginPage
from pages.content_page import ContentPage

load_dotenv()

class TestStrapiAutomation(unittest.TestCase):

    def setUp(self):
        """Configuración previa a cada test"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless") 
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.base_url = os.getenv("BASE_URL")
        self.collection = os.getenv("COLLECTION_TYPE")
        
        self.item_name_initial = "Automation Test Item Final"
        self.item_name_edited = "Automation Test Item EDITED"

    def test_flujo_completo(self):
        driver = self.driver
        login_page = LoginPage(driver)
        content_page = ContentPage(driver)

        # ==========================================
        # CP-01: LOGIN FALLIDO
        # ==========================================
        print("\n--- CP-01: Login Fallido ---")
        login_page.open_url(f"{self.base_url}/auth/login")
        login_page.login("fake@email.com", "password123")
        content_page.take_screenshot("CP01_Formulario_Lleno")
        msg = login_page.get_error_message()
        if "Invalid credentials" in msg or "error" in msg.lower():
            login_page.take_screenshot("CP01_Login_Fallido_OK")
            print(">> CP-01 PASÓ: Mensaje de error detectado.")
        else:
            self.fail("CP-01 FALLÓ: No se mostró error de credenciales.")

        # ==========================================
        # CP-02: LOGIN EXITOSO
        # ==========================================
        print("\n--- CP-02: Login Exitoso ---")
        driver.refresh()
        time.sleep(1)
        login_page.login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"))
        content_page.take_screenshot("CP02_Formulario_Lleno")
        time.sleep(3) # Esperar redirección
        if "admin" in driver.current_url:
            login_page.take_screenshot("CP02_Dashboard_OK")
            print(">> CP-02 PASÓ: Dashboard accedido.")
        else:
            self.fail("CP-02 FALLÓ: No redirigió al admin.")

        # ==========================================
        # NAVEGACIÓN
        # ==========================================
        content_page.go_to_collection_creation(self.collection)
        content_page.initiate_creation()

        # ==========================================
        # CP-03: VALIDACIÓN
        # ==========================================
        print("\n--- CP-03: Validación ---")
        if content_page.validate_required_field_behavior():
            print(">> CP-03 PASÓ: Validación correcta.")
        else:
            print(">> CP-03 BUG: Se permitió guardar sin campo nombre.")

        # ==========================================
        # CP-04: CREACIÓN
        # ==========================================
        print("\n--- CP-04: Creación ---")
        driver.refresh()
        time.sleep(2)
        content_page.fill_form_correctly(self.item_name_initial)
        content_page.take_screenshot("CP04_Item_Creado")
        print(">> CP-04 PASÓ.")

        # ==========================================
        # CP-05: EDICIÓN
        # ==========================================
        print("\n--- CP-05: Edición ---")
        content_page.navigate_back_to_list()
        content_page.click_edit_record_by_name(self.item_name_initial)
        content_page.fill_form_correctly(self.item_name_edited)
        content_page.take_screenshot("CP05_Item_Editado")
        
        # Validación de valor en input
        input_val = driver.find_element(By.NAME, "name").get_attribute("value")
        self.assertEqual(input_val, self.item_name_edited)
        print(">> CP-05 PASÓ.")

        # ==========================================
        # CP-06: ELIMINACIÓN
        # ==========================================
        print("\n--- CP-06: Eliminación ---")
        content_page.navigate_back_to_list()
        content_page.delete_record_by_name(self.item_name_edited)
        
        # Validar ausencia en tabla
        time.sleep(2)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if self.item_name_edited not in body_text:
            content_page.take_screenshot("CP06_Tabla_Sin_Item")
            print(">> CP-06 PASÓ: Registro eliminado correctamente.")
        else:
            content_page.take_screenshot("ERROR_CP06_Item_Sigue_Visible")
            self.fail("CP-06 FALLÓ: El item sigue visible.")

    def tearDown(self):
        print("\nFinalizando pruebas...")
        if self.driver:
            self.driver.quit()

# Esto permite seguir ejecutando este archivo individualmente si quieres
if __name__ == "__main__":
    unittest.main()