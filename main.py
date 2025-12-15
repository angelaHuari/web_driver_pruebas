import unittest
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Importar páginas
from pages.login_page import LoginPage
from pages.content_page import ContentPage

# Cargar variables
load_dotenv()

class TestStrapiAutomation(unittest.TestCase):

    def setUp(self):
        # Configuración del WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        
        # options.add_argument("--headless") # Descomentar para ejecución sin interfaz

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.base_url = os.getenv("BASE_URL")
        self.collection = os.getenv("COLLECTION_TYPE")

    def test_flujo_completo(self):
        driver = self.driver
        login_page = LoginPage(driver)
        content_page = ContentPage(driver)

        # ==========================================
        # PASO 1: LOGIN FALLIDO (Validación)
        # ==========================================
        print("\n--- PASO 1: Iniciando Test de Login Fallido ---")
        login_page.open_url(f"{self.base_url}/auth/login")
        login_page.login("fake@email.com", "password123")
        
        # ASSERT 1: Verificar el mensaje de error
        try:
            # Obtenemos el texto (Selenium esperará a que aparezca el ID global-form-error)
            error_msg = login_page.get_error_message()
            print(f">> Mensaje de error obtenido: '{error_msg}'")
            
            # Tomamos la foto INMEDIATAMENTE después de detectar el texto
            login_page.take_screenshot("2_error_login")
            
            # Validamos que el texto contenga "Invalid credentials"
            self.assertIn("Invalid credentials", error_msg, "El mensaje de error no coincide con lo esperado.")
            print(">> Validación de login fallido: CORRECTA")
            
        except Exception as e:
            print(f"ERROR: No se detectó el mensaje de error de login: {e}")
            login_page.take_screenshot("ERROR_mensaje_login_no_visto")
            raise e 
        
        # ==========================================
        # PASO 2: LOGIN EXITOSO
        # ==========================================
        print("\n--- PASO 2: Iniciando Login Correcto ---")
        driver.refresh() # Limpiamos el estado del formulario anterior
        time.sleep(1)
        login_page.login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"))
        
        # ASSERT 2: Verificar que estamos en el Dashboard
        time.sleep(3) # Espera para la transición de URL y carga del dashboard
        self.assertIn("admin", driver.current_url)
        print(">> Login Exitoso: Estamos en el Dashboard.")

        # ==========================================
        # PASO 3: NAVEGACIÓN Y CREACIÓN
        # ==========================================
        print("\n--- PASO 3: Navegando a Crear Contenido ---")
        content_page.go_to_collection_creation(self.collection)
        content_page.initiate_creation()

        # ==========================================
        # PASO 4: VALIDACIÓN DE FORMULARIO (CASO BUG)
        # ==========================================
        print("\n--- PASO 4: Probando Validación de Campos Requeridos ---")
        print(">> Intentando guardar solo con descripción para verificar si bloquea...")

        # Llamamos al método robusto que devuelve True (si validó bien) o False (si guardó el bug)
        is_validation_ok = content_page.validate_required_field_behavior()
        
        # ASSERT 3 (CRÍTICO): 
        # Si is_validation_ok es False, significa que se guardó sin nombre -> FALLA EL TEST
        self.assertTrue(is_validation_ok, 
                        "BUG CRÍTICO DETECTADO: El sistema permitió guardar una categoría SIN NOMBRE. "
                        "Revisar captura 'reports/screenshots/FALLO_BUG_permitio_guardar_sin_nombre.png'")
        
        print(">> ÉXITO: El sistema impidió guardar el registro vacío (Validación correcta).")

        # ==========================================
        # PASO 5: LLENADO Y GUARDADO EXITOSO
        # ==========================================
        print("\n--- PASO 5: Llenando Formulario Correctamente ---")
        
        # Refrescamos la página para asegurar un formulario limpio después de la prueba de error
        driver.refresh() 
        time.sleep(2)
        
        # Llenamos con datos válidos
        content_page.fill_form_correctly("Automation Test Item Final")
        
        # ASSERT 4: Verificar éxito final
        time.sleep(2)
        content_page.take_screenshot("5_item_creado_exito")
        
        # En Strapi, al guardar, la URL cambia de ".../create" a ".../id"
        url_suffix = driver.current_url.split('/')[-1]
        self.assertNotEqual("create", url_suffix, "La URL debería haber cambiado tras guardar exitosamente.")
        
        print(f">> Item creado correctamente. ID en URL: {url_suffix}")
        print("--- TEST FINALIZADO CON ÉXITO ---")

    def tearDown(self):
        print("\nCerrando navegador...")
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()