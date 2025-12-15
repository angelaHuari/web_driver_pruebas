from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
import time

class ContentPage(BasePage):
    # --- SELECTORES ---
    SKIP_TOUR_BTN = (By.XPATH, "//button[contains(., 'Skip')]")
    CREATE_ENTRY_BTN = (By.XPATH, "//a[contains(., 'Create new entry')]")
    
    # Inputs
    INPUT_NAME = (By.NAME, "name")
    INPUT_DESCRIPTION = (By.NAME, "description")
    
    # Botones y Alertas
    SAVE_BTN = (By.XPATH, "//button[@type='submit' and contains(., 'Save')]")
    
    # Selector para el mensaje verde de éxito (visible en tu imagen)
    SUCCESS_ALERT = (By.XPATH, "//div[contains(text(), 'Saved document')]")
    # Selector genérico de error (por si acaso lo arreglan en el futuro)
    ERROR_ALERT = (By.XPATH, "//div[contains(text(), 'required') or @data-strapi-field-error]")

    def go_to_collection_creation(self, collection_url_part):
        current_url = self.driver.current_url
        base = current_url.split('/admin')[0]
        target_url = f"{base}/admin/content-manager/collection-types/{collection_url_part}"
        print(f"--- Navegando a: {target_url} ---")
        self.open_url(target_url)
        print("Esperando carga de interfaz...")
        time.sleep(4) 

    def handle_onboarding_popup(self):
        """Maneja el popup de bienvenida si aparece"""
        try:
            skip_buttons = self.driver.find_elements(*self.SKIP_TOUR_BTN)
            if skip_buttons:
                print(f"Popup detectado. Cerrando con JS...")
                self.driver.execute_script("arguments[0].click();", skip_buttons[0])
                time.sleep(1)
            else:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass 

    def initiate_creation(self):
        self.handle_onboarding_popup()
        time.sleep(1) 
        print("Buscando enlace 'Create new entry'...")
        try:
            btns = self.wait.until(EC.presence_of_all_elements_located(self.CREATE_ENTRY_BTN))
            if len(btns) > 0:
                print(f"Click forzado en crear entrada.")
                self.driver.execute_script("arguments[0].click();", btns[0])
            else:
                raise TimeoutException("Lista de botones vacía")
        except TimeoutException:
            print("ERROR: No se encontró 'Create new entry'.")
            self.take_screenshot("ERROR_boton_crear")
            raise
    
    def fill_form_with_error(self):
        """
        Para probar el error, llenamos la descripción (opcional) pero dejamos el nombre vacío.
        Esto activa el botón 'Save' pero provoca el error de validación al hacer click.
        """
        print("--- Provocando error de validación ---")
        time.sleep(1)
        
        # 1. Escribimos en la DESCRIPCIÓN para "ensuciar" el formulario y habilitar el botón Save
        # Si no escribimos nada, el botón Save sigue disabled y Selenium falla.
        try:
            print("Escribiendo en descripción para habilitar botón...")
            self.send_keys(self.INPUT_DESCRIPTION, "Test para activar boton")
            time.sleep(1)
            
            # 2. Ahora el botón Save debería estar activo (sin atributo disabled)
            print("Haciendo click en Save (esperando error de Name)...")
            save_btn = self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN))
            save_btn.click()
            
            # 3. Tomamos captura del error (bordes rojos o mensaje)
            time.sleep(1)
            self.take_screenshot("3_validacion_error_campos")
            
        except TimeoutException:
            print("ERROR: El botón Save sigue deshabilitado o no se encontró.")
            self.take_screenshot("ERROR_save_disabled")
            raise

    def fill_form_correctly(self, text_value):
        print("--- Llenando formulario correctamente ---")
        time.sleep(1)
        # Llenamos el campo obligatorio NAME
        self.send_keys(self.INPUT_NAME, text_value)
        
        self.take_screenshot("4_formulario_contenido_lleno")
        
        # Click en guardar
        self.click(self.SAVE_BTN)
        print("Guardando...")
        time.sleep(3) # Esperamos a que guarde
