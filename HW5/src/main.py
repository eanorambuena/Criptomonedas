from block import FullBlock


# Implement the procedure to get the first 20 blocks of bitcoin's testnet here.
# The blocks should be returned as an ordered list starting from the original.
def main() -> list[FullBlock]:
    return []

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


if __name__ == '__main__':
    for b in main2():
        print(b)
