# Test para el subárbol 2 (hashes 5-8 del árbol original)
from Bitcoin_Merkle import SortedTree, str_human, print_tree, verify_non_inclusion

SUBTREE_HEX_HASHES = [
    "a7a4aec28e7162e1e9ef33dfa30f0bc0526e6cf4b11a576f6c5de58593898330",
    "bb6267664bd833fd9fc82582853ab144fece26b7a8a5bf328f8a059445b59add",
    "ea6d7ac1ee77fbacee58fc717b990c4fcccf1b19af43103c090f601677fd8836",
    "457743861de496c429912558a106b810b0507975a49773228aa788df40730d41",
]

subtree_hashes = [bytes.fromhex(h) for h in SUBTREE_HEX_HASHES]
sorted_tree_sub = SortedTree(subtree_hashes)

print("\n" + "="*60)
print("TEST SUBÁRBOL 2 - HASHES ORDENADOS")
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
