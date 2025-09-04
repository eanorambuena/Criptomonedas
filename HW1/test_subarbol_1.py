# Test para el subárbol 1 (primeros 4 hashes del árbol original)
from Bitcoin_Merkle import SortedTree, str_human, print_tree, verify_non_inclusion

SUBTREE_HEX_HASHES = [
    "9745f7173ef14ee4155722d1cbf13304339fd00d900b759c6f9d58579b5765fb",
    "5573c8ede34936c29cdfdfe743f7f5fdfbd4f54ba0705259e62f39917065cb9b",
    "82a02ecbb6623b4274dfcab82b336dc017a27136e08521091e443e62582e8f05",
    "507ccae5ed9b340363a0e6d765af148be9cb1c8766ccc922f83e4ae681658308",
]

subtree_hashes = [bytes.fromhex(h) for h in SUBTREE_HEX_HASHES]
sorted_tree_sub = SortedTree(subtree_hashes)

print("\n" + "="*60)
print("TEST SUBÁRBOL 1 - HASHES ORDENADOS")
print("="*60)
print_tree(sorted_tree_sub)

# Prueba de no inclusión
hash_modificado = subtree_hashes[0][:-1] + b'\x01'
proof_non = sorted_tree_sub.proof_of_non_inclusion(hash_modificado)
print(f"\nHash modificado: {hash_modificado.hex()[:16]}...")
print(f"¿Está incluido? {hash_modificado in sorted_tree_sub.hashes}")
print(f"Prueba generada: {proof_non is not None}")
if proof_non:
    print(f"Hashes en la prueba: {[str_human(h) for h in proof_non.hashes]}")
    print(f"Flags: {proof_non.flags}")
    print(f"Número de hojas: {proof_non.nrLeaves}")
    root = sorted_tree_sub.tree.root
    resultado = verify_non_inclusion(hash_modificado, root, proof_non)
    print(f"¿Verificación de no inclusión exitosa? {resultado}")

# Prueba de inclusión
proof_inc = sorted_tree_sub.proof_of_non_inclusion(subtree_hashes[0])
print(f"\nHash incluido: {subtree_hashes[0].hex()[:16]}...")
print(f"¿Está incluido? {subtree_hashes[0] in sorted_tree_sub.hashes}")
print(f"Prueba generada: {proof_inc} (debería ser None)")
