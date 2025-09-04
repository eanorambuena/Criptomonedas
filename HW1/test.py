from Bitcoin_Merkle import sorted_tree, raw_hashes, \
    str_human, print_tree

print("\n" + "="*60)
print("PRUEBA DE SORTED TREE - ÁRBOL ORDENADO PARA PRUEBAS DE NO INCLUSIÓN")
print("="*60)

print("\n1. HASHES ORDENADOS EN EL ÁRBOL:")
for i, h in enumerate(sorted_tree.hashes):
    name = sorted_tree.hash_to_name[h]
    print(f"   {name:<5} -> {h.hex()[:16]}...")

print("\n2. REPRESENTACIÓN DEL ÁRBOL MERKLE (EN FORMA DE TRIÁNGULO):")
print_tree(sorted_tree)

print("\n3. EXPLICACIÓN PASO A PASO DEL ALGORITMO:")
print("- El árbol Merkle ordenado se construye ordenando los hashes de las transacciones alfabéticamente.")
print("- Cada nodo tiene un nombre corto (a, b, c, ...) para facilitar la visualización.")
print("- Para una prueba de NO INCLUSIÓN de un hash H:")
print("  1. Verifica si H está en la lista ordenada de hashes.")
print("     - Si sí, retorna None (no hay prueba de no inclusión).")
print("     - Si no, encuentra los hashes adyacentes A (anterior) y B (siguiente) en la lista ordenada.")
print("  2. Genera una prueba de inclusión para A y B.")
print("     - Recorre el árbol desde A y B hacia la raíz, recolectando siblings (hermanos) necesarios.")
print("     - Usa DFS para asegurar minimalidad: solo incluye hashes y flags esenciales.")
print("  3. La prueba incluye flags (1 para incluir, 0 para omitir) y la lista de hashes necesarios.")
print("  4. Para verificar: si A y B están incluidos, y H no está entre ellos, entonces H no está incluido.")
print("- El árbol se imprime con indentación creciente desde las hojas (arriba) hacia la raíz (abajo).")

print("\n" + "-"*60)
print("5. PRUEBA DE NO INCLUSIÓN PARA UN HASH NO INCLUIDO")
print("-"*60)
# Hash no incluido: modificar uno existente
test_hash = raw_hashes[0][:-1] + b'\x01'  # Cambiar el último byte
proof_non = sorted_tree.proof_of_non_inclusion(test_hash)
print(f"   Hash de prueba (modificado de '{str_human(raw_hashes[0])}'): {test_hash.hex()[:16]}...")
print(f"   ¿Está incluido? {test_hash in sorted_tree.hashes}")
print(f"   Prueba generada: {proof_non is not None}")
if proof_non:
    print(f"   Hashes en la prueba: {[str_human(h) for h in proof_non.hashes]}")
    print(f"   Flags: {proof_non.flags}")
    print(f"   Número de hojas: {proof_non.nrLeaves}")

print("\n" + "-"*60)
print("6. PRUEBA DE NO INCLUSIÓN PARA UN HASH INCLUIDO")
print("-"*60)
# Hash incluido
proof_inc = sorted_tree.proof_of_non_inclusion(raw_hashes[0])
print(f"   Hash de prueba ('{str_human(raw_hashes[0])}'): {raw_hashes[0].hex()[:16]}...")
print(f"   ¿Está incluido? {raw_hashes[0] in sorted_tree.hashes}")
print(f"   Prueba generada: {proof_inc} (debería ser None, ya que está incluido)")

print("\n" + "="*60)
print("FIN DE LA PRUEBA")
print("="*60)