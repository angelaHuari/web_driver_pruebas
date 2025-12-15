from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from pages.base_page import BasePage
import time

class ContentPage(BasePage):
    # --- SELECTORES GENERALES ---
    SKIP_TOUR_BTN = (By.XPATH, "//button[contains(., 'Skip')]")
    CREATE_ENTRY_BTN = (By.XPATH, "//a[contains(., 'Create new entry')]")
    BACK_TO_LIST_BTN = (By.XPATH, "//a[contains(@href, '/content-manager/collection-types')]//span[contains(@class, 'arrow-left')] | //button[contains(., 'Back')]")
    
    # --- SELECTORES FORMULARIO ---
    INPUT_NAME = (By.NAME, "name")
    INPUT_DESCRIPTION = (By.NAME, "description")
    SAVE_BTN = (By.XPATH, "//button[@type='submit' and contains(., 'Save')]")
    
    # --- SELECTORES ALERTAS ---
    SUCCESS_TOAST = (
        By.XPATH,
        "//div[@role='status' and contains(., 'Saved document')]"
    )

    INPUT_ERROR_MSG = (By.XPATH, "//*[contains(text(), 'required') or contains(text(), 'must be defined')]")

    # --- SELECTORES TABLA ---
    DELETE_MENU_ITEM = (By.XPATH, "//div[@role='menuitem']//span[contains(text(), 'Delete')]")
    
    # CORRECCIÓN AQUÍ: Ajustado al HTML real (alertdialog y búsqueda profunda de texto)
    CONFIRM_DELETE_BTN = (By.XPATH, "//div[@role='alertdialog']//button[contains(., 'Confirm')]")

    def go_to_collection_creation(self, collection_url_part):
        current_url = self.driver.current_url
        base = current_url.split('/admin')[0]
        target_url = f"{base}/admin/content-manager/collection-types/{collection_url_part}"
        print(f"--- Navegando a: {target_url} ---")
        self.open_url(target_url)
        print("Esperando carga de interfaz...")
        time.sleep(4) 

    def handle_onboarding_popup(self):
        try:
            skip_buttons = self.driver.find_elements(*self.SKIP_TOUR_BTN)
            if skip_buttons:
                self.driver.execute_script("arguments[0].click();", skip_buttons[0])
                time.sleep(1)
            else:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass 

    def initiate_creation(self):
        self.handle_onboarding_popup()
        time.sleep(1) 
        try:
            btns = self.wait.until(EC.presence_of_all_elements_located(self.CREATE_ENTRY_BTN))
            if len(btns) > 0:
                self.driver.execute_script("arguments[0].click();", btns[0])
            else:
                raise TimeoutException("Lista de botones vacía")
        except TimeoutException:
            self.take_screenshot("ERROR_boton_crear")
            raise
    
    def validate_required_field_behavior(self):
        print("--- Verificando validación de campo requerido (Name) ---")
        time.sleep(1)
        self.send_keys(self.INPUT_DESCRIPTION, "Test validación - Sin Nombre")
        time.sleep(1)
        
        save_btn = self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN))
        save_btn.click()
        
        try:
            wait_short = WebDriverWait(self.driver, 3)
            wait_short.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
            self.take_screenshot("ERROR_BUG_permitio_guardar_sin_nombre")
            return False 
        except TimeoutException:
            try:
                wait_short = WebDriverWait(self.driver, 3)
                wait_short.until(EC.presence_of_element_located(self.INPUT_ERROR_MSG))
                self.take_screenshot("SUCCESS_validacion_correcta")
                return True 
            except TimeoutException:
                self.take_screenshot("WARNING_sin_feedback_visual")
                return True 

    def fill_form_correctly(self, text_value):
        print(f"--- Llenando formulario con: {text_value} ---")
        time.sleep(1)
        
        # 1. Limpiar y escribir
        input_elem = self.wait.until(EC.visibility_of_element_located(self.INPUT_NAME))
        input_elem.click()
        input_elem.clear()
        time.sleep(0.5) 
        input_elem.send_keys(text_value)
        
        time.sleep(1) 

        # 2. Click Seguro (Anti-Stale)
        print("Intentando guardar (con protección StaleElement)...")
        intentos = 0
        while intentos < 3:
            try:
                save_btn = self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN))
                save_btn.click()
                print("Click en Save exitoso.")
                break 
            except StaleElementReferenceException:
                print(f"Detectado elemento obsoleto (intento {intentos+1}). Reintentando...")
                intentos += 1
                time.sleep(1) 
            except Exception as e:
                print(f"Otro error al guardar: {e}")
                raise e
        time.sleep(2) 

    def navigate_back_to_list(self):
        try:
            print("Regresando a la lista de registros...")
            back_btn = self.driver.find_element(By.XPATH, "//header//button[contains(@aria-label, 'Back') or contains(., 'Back')] | //a[contains(@href, 'content-manager')]//span[contains(@class, 'arrow')]")
            back_btn.click()
        except Exception:
            self.driver.back()
        time.sleep(3)

    def click_edit_record_by_name(self, record_name):
        print(f"Buscando registro para editar: '{record_name}'")
        xpath_name = f"//tbody//tr//span[text()='{record_name}']"
        
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_name)))
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(0.5)
            element.click()
            print("Registro clickeado. Esperando formulario...")
            time.sleep(2)
        except TimeoutException:
            print(f"ERROR: No se encontró el registro '{record_name}' en la tabla.")
            self.take_screenshot("ERROR_registro_no_encontrado")
            raise

    def delete_record_by_name(self, record_name):
        print(f"Buscando registro para eliminar: '{record_name}'")
        xpath_row_action = f"//tbody//tr[contains(., '{record_name}')]//button[contains(., 'Row actions')]"
        
        try:
            # 1. Scroll para asegurar que la fila es visible
            row_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_row_action)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row_btn)
            time.sleep(0.5)
            
            # 2. Click en los 3 puntos
            btn_action = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_row_action)))
            btn_action.click()
            time.sleep(1)

            # 3. Click Borrar en el menú flotante
            delete_opt = self.wait.until(EC.element_to_be_clickable(self.DELETE_MENU_ITEM))
            delete_opt.click()
            print("Menú Delete clickeado. Esperando Modal...")
            time.sleep(5) 
            self.take_screenshot("7_modal_de_eliminacion_abierto")
            
            # 4. Confirmar en el Modal (CORREGIDO)
            print("Confirmando eliminación en Modal...")
            # Aumentamos el wait a 5s para dar tiempo a la animación del modal
            confirm_btn = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.CONFIRM_DELETE_BTN))
            confirm_btn.click()
            time.sleep(2) 
            
        except TimeoutException:
            print("ERROR: Fallo en el flujo de eliminación. El botón 'Confirm' no apareció o no fue clickeable.")
            self.take_screenshot("ERROR_flujo_eliminacion")
            raise
    
    def is_text_present_in_body(self, text):
        return text in self.driver.find_element(By.TAG_NAME, "body").text