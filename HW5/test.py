import unittest
import sys
import os

# --- Configuración de Ruta ---
# Añadimos la carpeta 'uw' (que está al mismo nivel que este script)
# al path de Python para que podamos importar 'main', 'block', etc.
# Si tu carpeta se llama diferente a 'uw', cambia 'uw' por el nombre correcto.
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src') 
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# --- Importaciones del Proyecto ---
# Estas importaciones ahora deberían funcionar gracias al sys.path
try:
    from main import main
    from block import FullBlock, Block
    from txP2PKH import Tx
    from helper import hash256
except ImportError as e:
    print(f"Error: No se pudo importar el módulo. Asegúrate de que este script esté")
    print(f"en el directorio padre de tu carpeta de código (ej: 'uw'). Error: {e}")
    sys.exit(1)

# --- Constantes de Prueba ---
# Este es el hash conocido del bloque génesis de tu testnet
# Lo usamos para verificar el primer bloque.
TESTNET_GENESIS_HASH = "000000000933ea01ad0ee984209779baaec3ced90fa3f408719526f8d77f4943"

# Un 'TestCase' que agrupa todas nuestras pruebas para la Tarea 4
class TestTarea4(unittest.TestCase):

    # Variable de clase para guardar los bloques.
    # Usamos @classmethod para ejecutar main() UNA SOLA VEZ
    # y no descargar los 20 bloques por cada test.
    @classmethod
    def setUpClass(cls):
        """
        Este método se ejecuta una vez antes de todas las pruebas.
        Descarga los bloques y los guarda en 'cls.blocks'.
        """
        print("Iniciando prueba: Descargando los 20 bloques... (esto puede tardar un momento)")
        try:
            cls.blocks = main()
            print("Descarga completada. Ejecutando aserciones...")
        except Exception as e:
            # Si main() falla, no podemos ejecutar ninguna prueba.
            raise Exception(f"La ejecución de main() falló. Error: {e}")

    # --- Pruebas para la Parte 1 ---
    
    def test_part1_main_returns_list(self):
        """
        Prueba (Parte 1): Verifica que main() retorna una lista.
        """
        self.assertIsInstance(self.blocks, list, "La función main() no retornó una lista.")

    def test_part1_main_returns_20_blocks(self):
        """
        Prueba (Parte 1): Verifica que la lista contiene exactamente 20 bloques.
        """
        self.assertEqual(len(self.blocks), 20, f"Se esperaban 20 bloques, pero se recibieron {len(self.blocks)}.")

    def test_part1_items_are_fullblocks(self):
        """
        Prueba (Parte 1): Verifica que todos los ítems en la lista son objetos 'FullBlock'.
        """
        self.assertIsInstance(self.blocks[0], FullBlock, "El primer ítem no es un objeto FullBlock.")
        self.assertIsInstance(self.blocks[19], FullBlock, "El último ítem no es un objeto FullBlock.")

    def test_part1_genesis_block_is_correct(self):
        """
        Prueba (Parte 1): Verifica que el primer bloque (bloque original) es correcto.
        Compara su hash con el hash conocido de la testnet.
        """
        genesis_block = self.blocks[0]
        self.assertEqual(genesis_block.hash().hex(), TESTNET_GENESIS_HASH, "El hash del bloque génesis no coincide.")

    def test_part1_blocks_are_chained_correctly(self):
        """
        Prueba (Parte 1): Verifica que la lista está "ordenada".
        Comprueba que el 'prev_block' de cada bloque coincide con el hash de su predecesor.
        """
        # Iteramos desde el bloque 1 hasta el 19
        for i in range(1, 20):
            current_block = self.blocks[i]
            previous_block = self.blocks[i-1]
            
            with self.subTest(i=i): # reportará el índice exacto si falla
                self.assertEqual(
                    current_block.prev_block, 
                    previous_block.hash(),
                    f"El enlace se rompe en el Bloque #{i}: prev_block no coincide con el hash del Bloque #{i-1}."
                )

    def test_part1_blocks_have_transactions(self):
        """
        Prueba (Parte 1): Verifica que los bloques descargados son "bloques enteros".
        Comprueba que los bloques *descargados* (ej. el bloque #1) contienen transacciones.
        """
        # El bloque 0 (génesis) fue cargado manualmente sin txs, 
        # así que probamos el bloque 1 (el primero descargado).
        first_downloaded_block = self.blocks[1]
        
        self.assertIsInstance(first_downloaded_block.txs, list, "Bloque #1 no tiene una lista de txs.")
        
        # Debe tener al menos una transacción (la coinbase)
        self.assertGreater(
            len(first_downloaded_block.txs), 0, 
            "El Bloque #1 se descargó sin transacciones."
        )
        
        # Verifica que el contador 'nr_trans' coincida 
        # con las transacciones parseadas
        self.assertEqual(
            first_downloaded_block.nr_trans,
            len(first_downloaded_block.txs),
            "El contador 'nr_trans' no coincide con el número de transacciones parseadas en el Bloque #1."
        )

    # --- Pruebas para la Parte 2 ---

    def test_part2_validation_fails_as_expected(self):
        """
        Prueba (Parte 2): Verifica que la validación de la coinbase TX falla como se espera.
        Intenta validar la coinbase TX del primer bloque *descargado* (Bloque #1)
        y espera un 'ValueError' específico, como se explica en el README.
        """
        block_to_test = self.blocks[1] # Usamos el primer bloque *descargado*
        coinbase_tx = block_to_test.txs[0] # La tx coinbase es siempre la primera

        print("\nPrueba (Parte 2): Intentando validar la coinbase TX (se espera un error)...")
        
        # Usamos assertRaises para verificar que la operación *falla*
        with self.assertRaises(Exception, msg="coinbase_tx.verify() no lanzó ninguna excepción.") as context:
            coinbase_tx.verify() # Esta línea debe fallar

        # Verifica que el error es el esperado
        # El error raíz es un ValueError de TxFetcher
        self.assertIsInstance(
            context.exception, 
            ValueError, 
            f"El error esperado era 'ValueError', pero fue '{type(context.exception).__name__}'."
        )
        
        # Verifica el mensaje de error específico
        expected_error_message = "unexpected response"
        self.assertIn(
            expected_error_message, 
            str(context.exception),
            f"El mensaje de error no contiene '{expected_error_message}'."
        )
        
        print("-> Prueba (Parte 2) exitosa: La validación falló con el error esperado.")


# --- Ejecutor de Pruebas ---
if __name__ == '__main__':
    # Esto permite ejecutar el script directamente
    # -v habilita la verbosidad para ver los nombres de las pruebas
    unittest.main(argv=['first-arg-is-ignored', '-v'])
