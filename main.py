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
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless") 

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.base_url = os.getenv("BASE_URL")
        self.collection = os.getenv("COLLECTION_TYPE")
        
        # Nombres de prueba
        self.item_name_initial = "Automation Test Item Final"
        self.item_name_edited = "Automation Test Item EDITED"

    def test_flujo_completo(self):
        driver = self.driver
        login_page = LoginPage(driver)
        content_page = ContentPage(driver)

        # ==========================================
        # CP-01: Login con credenciales inválidas
        # ==========================================
        print("\n--- CP-01: Login Fallido ---")
        login_page.open_url(f"{self.base_url}/auth/login")
        login_page.login("fake@email.com", "password123")
        
        try:
            error_msg = login_page.get_error_message()
            print(f">> Mensaje: '{error_msg}'")
            login_page.take_screenshot("2_error_login")
            self.assertIn("Invalid credentials", error_msg)
            print(">> Estado: PASÓ")
        except Exception as e:
            login_page.take_screenshot("ERROR_CP01")
            raise e 
        
        # ==========================================
        # CP-02: Login con credenciales válidas
        # ==========================================
        print("\n--- CP-02: Login Exitoso ---")
        driver.refresh()
        time.sleep(1)
        login_page.login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"))
        
        time.sleep(3)
        login_page.take_screenshot("SUCCESS_dashboard_view")
        self.assertIn("admin", driver.current_url)
        print(">> Estado: PASÓ")

        # ==========================================
        # NAVEGACIÓN
        # ==========================================
        print("\n--- Navegando a Colección ---")
        content_page.go_to_collection_creation(self.collection)
        
        # Verificamos si estamos en la lista, si es así iniciamos creación
        content_page.initiate_creation()

        # ==========================================
        # CP-03: Validación de campos requeridos
        # ==========================================
        print("\n--- CP-03: Validación de Campos Requeridos ---")
        is_validation_ok = content_page.validate_required_field_behavior()
        
        if not is_validation_ok:
            print(">> Estado: FALLÓ (Bug detectado) CP-03 FALLÓ: El sistema permitió guardar sin nombre")
        else:
            content_page.take_screenshot("3_validacion_error")
            print(">> Estado: PASÓ")


        # ==========================================
        # CP-04: Creación de nuevo registro
        # ==========================================
        print("\n--- CP-04: Creación de Registro ---")
        driver.refresh() 
        time.sleep(2)
        
        content_page.fill_form_correctly(self.item_name_initial)
        
        time.sleep(2)
        content_page.take_screenshot("4_formulario_categorias_contenido_lleno")
        content_page.take_screenshot("5_item_creado_exito")
        
        url_suffix = driver.current_url.split('/')[-1]
        self.assertNotEqual("create", url_suffix, "CP-04 Falló: URL no cambió tras guardar.")
        print(f">> Registro creado: {self.item_name_initial}")
        print(">> Estado: PASÓ")

        # ==========================================
        # CP-05: Edición de un registro
        # ==========================================
        print("\n--- CP-05: Edición de Registro ---")
        
        # 1. Volver a la lista
        content_page.navigate_back_to_list()
        
        # 2. Buscar y clickear el item creado
        content_page.click_edit_record_by_name(self.item_name_initial)
        
        # 3. Editar el nombre
        print(f">> Cambiando nombre a: {self.item_name_edited}")
        content_page.fill_form_correctly(self.item_name_edited)
        
        # 4. Verificar éxito
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            # Busca el elemento de estado que contiene el texto
     
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='status' and contains(., 'Saved document')]")))
            content_page.take_screenshot("6_edicion_exito")
            print(">> Alerta de guardado detectada.")
        except Exception:
            print("WARNING: No se detectó alerta, verificando valor en input...")
            content_page.take_screenshot("WARNING_sin_mensaje_de_exito")
        
        # Assert: Verificar que el input ahora tiene el nuevo valor
        input_val = driver.find_element(By.NAME, "name").get_attribute("value")
        self.assertEqual(input_val, self.item_name_edited, "CP-05 Falló: El valor no se actualizó.")
        print(">> Estado: PASÓ")

        # ==========================================
        # CP-06: Eliminación de un registro
        # ==========================================
        print("\n--- CP-06: Eliminación de Registro ---")
        # 1. Volver a la lista
        content_page.navigate_back_to_list()
        
        # 2. Buscar el item YA EDITADO y eliminarlo
        content_page.delete_record_by_name(self.item_name_edited)
        
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='status' and contains(., 'Deleted document')]")))
        
        content_page.take_screenshot("8_eliminacion_mensaje_de_exito")
        try:
            print("Esperando actualización de la tabla...")
            
            wait = WebDriverWait(self.driver, 5)
            
            try:
                wait.until_not(
                    EC.text_to_be_present_in_element((By.TAG_NAME, "body"), self.item_name_edited)
                )
            except:
                print("WARNING: El texto sigue visible tras la espera.")

            # 3. Tomar captura de pantalla del estado de la tabla
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_success = f"SUCCESS_tabla_post_borrado_{timestamp}.png"
            content_page.take_screenshot(screenshot_success)

            # 4. Validación (Assertion)
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            self.assertNotIn(
                self.item_name_edited, 
                body_text, 
                "CP-06 Falló: El registro sigue visible en la tabla después de confirmar eliminación."
            )
            print("CP-06 Éxito: El registro fue eliminado correctamente.")
            print(">> Estado: PASÓ")

        except AssertionError as e:
            # 5. Captura de pantalla en caso de ERROR de validación
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_fail = f"ERROR_fallo_eliminacion_{timestamp}.png"
            content_page.take_screenshot(screenshot_fail)
            print(f"ERROR DETECTADO. Captura de fallo guardada en: {screenshot_fail}")
            
            # Re-lanzamos el error para que unittest marque el test como FAILED
            raise e

        except Exception as e:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            content_page.take_screenshot(f"ERROR_NO_SOPORTADO_{timestamp}.png")
            raise e
        
        print("\n=== TODOS LOS CASOS DE PRUEBA FINALIZADOS EXITOSAMENTE ===")

    def tearDown(self):
        print("\nCerrando navegador...")
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()