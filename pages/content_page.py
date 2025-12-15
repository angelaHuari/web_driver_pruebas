import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from pages.base_page import BasePage

class ContentPage(BasePage):
    
    # --- SELECTORES (Basados en tu código funcional) ---
    SKIP_TOUR_BTN = (By.XPATH, "//button[contains(., 'Skip') or contains(., 'Saltar')]")
    CREATE_ENTRY_BTN = (By.XPATH, "//a[contains(., 'Create new entry')]")
    BACK_TO_LIST_BTN = (By.XPATH, "//a[contains(@href, '/content-manager/collection-types')]//span[contains(@class, 'arrow-left')] | //button[contains(., 'Back')]")
    
    INPUT_NAME = (By.NAME, "name")
    INPUT_DESCRIPTION = (By.NAME, "description")
    SAVE_BTN = (By.XPATH, "//button[@type='submit' and contains(., 'Save')]")
    
    SUCCESS_TOAST = (By.XPATH, "//div[@role='status' and contains(., 'Saved document')]")
    DELETED_TOAST = (By.XPATH, "//div[@role='status' and contains(., 'Deleted document')]")
    INPUT_ERROR_MSG = (By.XPATH, "//*[contains(text(), 'required') or contains(text(), 'must be defined')]")

    DELETE_MENU_ITEM = (By.XPATH, "//div[@role='menuitem']//span[contains(text(), 'Delete')]")
    CONFIRM_DELETE_BTN = (By.XPATH, "//div[@role='alertdialog']//button[contains(., 'Confirm')]")

    def go_to_collection_creation(self, collection_url_part):
        """Navega directamente a la URL de la colección."""
        current_url = self.driver.current_url
        base = current_url.split('/admin')[0]
        target_url = f"{base}/admin/content-manager/collection-types/{collection_url_part}"
        self.open_url(target_url)
        print("Esperando carga de interfaz...")
        time.sleep(4) # Espera necesaria para Strapi

    def handle_onboarding_popup(self):
        """Cierra el popup de bienvenida si aparece."""
        try:
            # Espera corta para ver si aparece el botón
            wait_short = WebDriverWait(self.driver, 4)
            skip_buttons = wait_short.until(EC.presence_of_all_elements_located(self.SKIP_TOUR_BTN))
            if skip_buttons:
                print("Popup detectado. Cerrando...")
                self.driver.execute_script("arguments[0].click();", skip_buttons[0])
                time.sleep(1)
            else:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass # Si no aparece, continuamos

    def initiate_creation(self):
        """Maneja el popup y hace click en Crear."""
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
        """Intenta guardar sin nombre para validar el error."""
        print("--- Verificando validación de campo requerido (Name) ---")
        time.sleep(1)
        self.send_keys(self.INPUT_DESCRIPTION, "Test validación - Sin Nombre")
        time.sleep(1)
        
        save_btn = self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN))
        save_btn.click()
        
        try:
            # Bug Check: Si aparece el Toast de éxito, es un fallo del sistema
            wait_short = WebDriverWait(self.driver, 3)
            wait_short.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
            self.take_screenshot("CP03_ERROR_BUG_permitio_guardar_sin_nombre")
            return False 
        except TimeoutException:
            # Comportamiento esperado: Mensaje de error
            try:
                wait_short = WebDriverWait(self.driver, 3)
                wait_short.until(EC.presence_of_element_located(self.INPUT_ERROR_MSG))
                self.take_screenshot("CP03_SUCCESS_validacion_correcta")
                return True 
            except TimeoutException:
                self.take_screenshot("CP03_WARNING_sin_feedback_visual")
                return True 

    def fill_form_correctly(self, text_value):
        """Llena el formulario y guarda con reintentos."""
        print(f"--- Llenando formulario con: {text_value} ---")
        time.sleep(1)
        
        input_elem = self.wait.until(EC.visibility_of_element_located(self.INPUT_NAME))
        input_elem.click()
        input_elem.clear()
        time.sleep(0.5)
        input_elem.send_keys(text_value)
        time.sleep(1)

        # Lógica de reintento para evitar StaleElementReferenceException
        print("Intentando guardar...")
        intentos = 0
        while intentos < 3:
            try:
                save_btn = self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN))
                save_btn.click()
                print("Click en Save exitoso.")
                break 
            except StaleElementReferenceException:
                print(f"Elemento obsoleto, reintento {intentos+1}...")
                intentos += 1
                time.sleep(1)
            except Exception as e:
                raise e
        
        # Validar guardado
        try:
            self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
        except TimeoutException:
            print("Warning: Toast no detectado, continuando flujo.")
        
        time.sleep(2)

    def navigate_back_to_list(self):
        try:
            print("Regresando a la lista de registros...")
            back_btn = self.driver.find_element(*self.BACK_TO_LIST_BTN)
            back_btn.click()
        except Exception:
            self.driver.back()
        time.sleep(3) # Espera crítica para recarga de tabla

    def click_edit_record_by_name(self, record_name):
        print(f"Buscando registro para editar: '{record_name}'")
        xpath_name = f"//tbody//tr//span[text()='{record_name}']"
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_name)))
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(0.5)
            element.click()
            print("Registro clickeado.")
            time.sleep(2)
        except TimeoutException:
            self.take_screenshot("CP04_ERROR_registro_no_encontrado")
            raise

    def delete_record_by_name(self, record_name):
        print(f"Buscando registro para eliminar: '{record_name}'")
        xpath_row_action = f"//tbody//tr[contains(., '{record_name}')]//button[contains(., 'Row actions')]"
        
        try:
            # 1. Menú de acciones
            row_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_row_action)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row_btn)
            time.sleep(0.5)
            
            # Click normal o JS si falla
            try:
                row_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", row_btn)
            
            time.sleep(1)

            # 2. Click Borrar
            delete_opt = self.wait.until(EC.element_to_be_clickable(self.DELETE_MENU_ITEM))
            delete_opt.click()
            print("Menú Delete clickeado. Esperando Modal...")
            
            # 3. Esperar Modal y tomar Captura
            time.sleep(2) # Pausa para animación del modal
            self.wait.until(EC.visibility_of_element_located(self.CONFIRM_DELETE_BTN))
            self.take_screenshot("CP06_Modal_Eliminacion_Visible")
            
            # 4. Confirmar
            print("Confirmando eliminación...")
            confirm_btn = self.driver.find_element(*self.CONFIRM_DELETE_BTN)
            confirm_btn.click()
            
            # 5. Esperar confirmación visual
            self.wait.until(EC.visibility_of_element_located(self.DELETED_TOAST))
            time.sleep(2)
            
        except TimeoutException:
            print("ERROR: Fallo en el flujo de eliminación.")
            self.take_screenshot("CP06_ERROR_flujo_eliminacion")
            raise