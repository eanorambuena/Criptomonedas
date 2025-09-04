# Test para el subárbol 4 (hashes 13-16 del árbol original)
from Bitcoin_Merkle import SortedTree, str_human, print_tree, verify_non_inclusion

SUBTREE_HEX_HASHES = [
    "b5c0b915312b9bdaedd2b86aa2d0f8feffc73a2d37668fd9010179261e25e263",
    "c9d52c5cb1e557b92c84c52e7c4bfbce859408bedffc8a5560fd6e35e10b8800",
    "c555bc5fc3bc096df0a0c9532f07640bfb76bfe4fc1ace214b8b228a1297a4c2",
    "f9dbfafc3af3400954975da24eb325e326960a25b87fffe23eef3e7ed2fb610e",
]

subtree_hashes = [bytes.fromhex(h) for h in SUBTREE_HEX_HASHES]
sorted_tree_sub = SortedTree(subtree_hashes)

print("\n" + "="*60)
print("TEST SUBÁRBOL 4 - HASHES ORDENADOS")
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
