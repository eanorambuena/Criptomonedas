from block import FullBlock, Block, TESTNET_GENESIS_BLOCK
from io import BytesIO
from network import SimpleNode, GetHeadersMessage, HeadersMessage, GetDataMessage, BLOCK_DATA_TYPE, BlockMessage


def main2() -> list[FullBlock]:
    from io import BytesIO
    from block import Block, TESTNET_GENESIS_BLOCK
    print("--- PASO 1: Cargando Bloque Génesis (Manual) ---")
    
    # La constante TESTNET_GENESIS_BLOCK es solo el header (80 bytes).
    # No podemos usar FullBlock.parse() en él porque faltan las TXs.
    # Usaremos Block.parse() solo para leer el header.
    
    try:
        stream = BytesIO(TESTNET_GENESIS_BLOCK)
        header = Block.parse(stream)
        
        # Ahora, creamos un objeto FullBlock "a mano".
        # Sabemos que el bloque génesis tiene 1 tx (la coinbase),
        # pero no la tenemos. Dejamos la lista txs vacía por ahora.
        # Solo necesitamos el objeto para que .hash() funcione.
        genesis_block = FullBlock(
            version=header.version,
            prev_block=header.prev_block,
            merkle_root=header.merkle_root,
            timestamp=header.timestamp,
            bits=header.bits,
            nonce=header.nonce,
            nr_trans=1,  # Lo sabemos por definición
            txs=[]       # Lo dejamos vacío, .hash() no lo usa
        )
        
        # Esta prueba ahora depende de FullBlock.serialize()
        hash_obtenido = genesis_block.hash().hex()
        print(f"Carga manual exitosa. Hash: {hash_obtenido}")
        
        # Este es el hash conocido del bloque génesis de testnet
        hash_conocido = "000000000933ea01ad0ee984209779baaec3ced90fa3f408719526f8d77f4943"
        
        if hash_obtenido == hash_conocido:
             print("¡Hash coincide con el esperado!")
             print("Esto prueba que FullBlock.serialize() es correcto.")
             print("--- PASO 1 SUPERADO ---")
             return [genesis_block] # Devolvemos el bloque para el siguiente paso
        else:
            print(f"ERROR: Hash no coincide. Obtenido: {hash_obtenido}")
            print(f"                           Esperado: {hash_conocido}")
            print("Revisa tu implementación de FullBlock.serialize() en block.py")
            return []

    except Exception as e:
        print(f"ERROR durante la carga manual: {e}")
        return []

# Implement the procedure to get the first 20 blocks of bitcoin's testnet here.
# The blocks should be returned as an ordered list starting from the original.
def main() -> list[FullBlock]:
    # --- PASO 1: Cargar Bloque Génesis ---
    print("--- PASO 1: Cargando Bloque Génesis (Local) ---")
    stream = BytesIO(TESTNET_GENESIS_BLOCK)
    header = Block.parse(stream)
    genesis_block = FullBlock(
        version=header.version,
        prev_block=header.prev_block,
        merkle_root=header.merkle_root,
        timestamp=header.timestamp,
        bits=header.bits,
        nonce=header.nonce,
        nr_trans=1,  # Dato simbólico
        txs=[]       # No se usa para el hash
    )
    
    print(f"Bloque 0 (Génesis) cargado. Hash: {genesis_block.hash().hex()}")
    
    blocks = [genesis_block]
    current_hash = genesis_block.hash()

    # --- PASO 3: Conectar y descargar los 19 bloques restantes ---
    print("\n--- PASO 3: Conectando a la Testnet ---")
    node = SimpleNode('testnet.programmingbitcoin.com', testnet=True, logging=False)
    try:
        node.handshake()
        print("¡Handshake exitoso!")

        # Bucle para descargar los bloques 1 al 19 (total 20)
        for i in range(19):
            print(f"\nDescargando bloque #{i+1}...")
            
            # 1. Pedir el siguiente header
            print("  1. Pidiendo header...")
            getheaders = GetHeadersMessage(start_block=current_hash)
            node.send(getheaders)
            headers_msg = node.wait_for(HeadersMessage)
            
            # 2. Obtener el hash del siguiente bloque
            next_hash = headers_msg.blocks[0].hash()
            print(f"  2. Hash obtenido: {next_hash.hex()}")
            
            # 3. Pedir el bloque completo (¡Prueba tu GetDataMessage.serialize!)
            print("  3. Pidiendo bloque completo (getdata)...")
            getdata = GetDataMessage()
            getdata.add_data(BLOCK_DATA_TYPE, next_hash) # BLOCK_DATA_TYPE es 2
            node.send(getdata)
            
            # 4. Recibir el bloque (¡Prueba tu BlockMessage.parse y FullBlock.parse!)
            print("  4. Esperando respuesta (block)...")
            block_msg = node.wait_for(BlockMessage)
            
            if block_msg.block:
                print(f"¡Bloque #{i+1} recibido y parseado!")
                print(f"   - Transacciones en el bloque: {block_msg.block.nr_trans}")
                blocks.append(block_msg.block)
                current_hash = next_hash
            else:
                print(f"ERROR: El nodo no envió un bloque válido para el bloque #{i+1}")
                break

    except Exception as e:
        print(f"\nERROR DE RED O PARSEO: {e}")
        print("Revisa la implementación de tus Pasos 1 y 2.")
        print("Asegúrate de tener todas las importaciones correctas en block.py y network.py")
        return []

    print(f"\n--- Descarga Completa ---")
    print(f"Total de bloques en memoria: {len(blocks)}")
    
    return blocks

if __name__ == '__main__':
    
    all_blocks = main()
    
    if len(all_blocks) == 20:
        print("\n--- TASK (Point 1) COMPLETE! ---")
        print("Downloaded 20 blocks successfully.")
        
        # --- START TASK (Point 2) ---
        print("\n--- Step 4 (Point 2): Attempting to validate transactions ---")
        print("Attempting to validate the first transaction (Coinbase) of the *first downloaded block* (Block #1)...")
        
        try:
            # CORRECCIÓN: Usamos all_blocks[1] (el primer bloque descargado)
            # en lugar de all_blocks[0] (el génesis manual).
            block_to_test = all_blocks[1] 
            
            # The first transaction (index 0) is always the coinbase
            coinbase_tx = block_to_test.txs[0]
            
            print(f"\nValidating TX: {coinbase_tx.id()} from Block {block_to_test.hash().hex()}")
            
            # This is where the failure is expected
            verification_result = coinbase_tx.verify()
            print(f"Transaction verification result: {verification_result}")
            
            print("Unexpected Success! The transaction verified correctly.")

        except Exception as e:
            print("\n\n*************************************************")
            print("       VALIDATION ERROR DETECTED (Expected)!")
            print("*************************************************")
            print(f"\nThe error was: {type(e).__name__}: {e}")
            print("\nThis confirms the expected behavior for Point 2 of the task.")
            raise e
        # --- END TASK (Point 2) ---

    else:
        print(f"\nDownload failed. Got {len(all_blocks)}/20 blocks.")
