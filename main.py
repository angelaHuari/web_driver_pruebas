import unittest
import os
import sys

# 1. Configuración Global (Logs y Rutas)
# Esto elimina los logs de WebDriver Manager antes de que se cargue cualquier otra cosa
os.environ['WDM_LOG'] = '0'

# Aseguramos que el directorio raíz esté en el path de Python
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_all_tests():
    """
    Descubre y ejecuta todos los tests en la carpeta 'tests'
    que coincidan con el patrón 'test_*.py'.
    """
    # 2. Cargar los tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    
    # Busca archivos que empiecen con 'test_' dentro de la carpeta 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 3. Ejecutar los tests
    # verbosity=2 muestra detalles de cada test (OK/FAIL) en la consola
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 4. Salida del sistema
    # Retorna código de error si falló algún test (útil para CI/CD)
    sys.exit(not result.wasSuccessful())

if __name__ == "__main__":
    print("Iniciando Pruebas Automatizadas...")
    run_all_tests()