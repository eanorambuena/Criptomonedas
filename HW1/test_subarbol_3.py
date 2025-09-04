# Test para el subárbol 3 (hashes 9-12 del árbol original)
from Bitcoin_Merkle import SortedTree, str_human, print_tree, verify_non_inclusion

SUBTREE_HEX_HASHES = [
    "7688029288efc9e9a0011c960a6ed9e5466581abf3e3a6c26ee317461add619a",
    "b1ae7f15836cb2286cdd4e2c37bf9bb7da0a2846d06867a429f654b2e7f383c9",
    "9b74f89fa3f93e71ff2c241f32945d877281a6a50a6bf94adac002980aafe5ab",
    "b3a92b5b255019bdaf754875633c2de9fec2ab03e6b8ce669d07cb5b18804638",
]

subtree_hashes = [bytes.fromhex(h) for h in SUBTREE_HEX_HASHES]
sorted_tree_sub = SortedTree(subtree_hashes)

print("\n" + "="*60)
print("TEST SUBÁRBOL 3 - HASHES ORDENADOS")
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
