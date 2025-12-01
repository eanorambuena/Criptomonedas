#!/usr/bin/env python3
# Solución Tarea 4 - IIC3272
# Sistema de billetera Bitcoin con soporte P2PKH y P2SH

from ecc import PrivateKey
from base58 import hash256, hash160, encode_base58_checksum
from scriptSimplified import p2pkh_script_from_address, p2sh_script_from_address, Script, p2pkh_script
from txWithP2SH import Tx, TxIn, TxOut

print("="*60)
print("TAREA 4 - IIC3272 - Sistema de Billetera Bitcoin")
print("="*60)

# =============================================================================
# PARTE 1: Generar las direcciones
# =============================================================================
print("\n" + "="*60)
print("PARTE 1: Generación de Direcciones P2PKH")
print("="*60)

# Generar dirección 1
secret1 = hash256(b'IIC3272SuNombre1')
intSecret1 = int(secret1.hex(), 16)
privKey1 = PrivateKey(intSecret1)
address1 = privKey1.point.address(compressed=True, testnet=True)

print(f"\nDirección 1:")
print(f"  Llave secreta (hex): {secret1.hex()}")
print(f"  Llave secreta (int): {intSecret1}")
print(f"  Dirección P2PKH: {address1}")

# Generar dirección 2
secret2 = hash256(b'IIC3272SuNombre2')
intSecret2 = int(secret2.hex(), 16)
privKey2 = PrivateKey(intSecret2)
address2 = privKey2.point.address(compressed=True, testnet=True)

print(f"\nDirección 2:")
print(f"  Llave secreta (hex): {secret2.hex()}")
print(f"  Llave secreta (int): {intSecret2}")
print(f"  Dirección P2PKH: {address2}")

print(f"\n{'='*60}")
print("INSTRUCCIONES PARA PARTE 1:")
print(f"{'='*60}")
print(f"1. Ve a https://coinfaucet.eu/en/btc-testnet/")
print(f"2. Solicita testcoins DOS VECES a la dirección 1: {address1}")
print(f"3. Verifica en https://live.blockcypher.com/btc-testnet/address/{address1}/")
print(f"4. Anota los tx_hash y tx_index de las dos transacciones recibidas")

# =============================================================================
# PARTE 2: Transacción P2PKH a P2PKH (2 inputs -> 1 output)
# =============================================================================
print("\n" + "="*60)
print("PARTE 2: Transacción P2PKH a P2PKH")
print("="*60)

print("\nPara ejecutar la Parte 2, necesitas:")
print("1. tx_hash_1 y tx_index_1 de la primera transacción recibida")
print("2. tx_hash_2 y tx_index_2 de la segunda transacción recibida")
print("\nEjemplo de código:")
print("""
# CONFIGURAR ESTOS VALORES CON TUS DATOS REALES:
tx_hash_1 = 'TU_TX_HASH_1_AQUI'
tx_index_1 = 0  # usualmente 0 o 1
tx_hash_2 = 'TU_TX_HASH_2_AQUI'  
tx_index_2 = 0  # usualmente 0 o 1

# Crear los inputs
input1 = TxIn(bytes.fromhex(tx_hash_1), tx_index_1)
input2 = TxIn(bytes.fromhex(tx_hash_2), tx_index_2)

# Crear el output a dirección 2
script_pubkey = p2pkh_script_from_address(address2)
# Calcular el monto (suma de inputs - fee)
# Si recibiste 10000 satoshis en cada tx, total = 20000
# Deja ~2000 para fee, output = 18000
output_amount = 18000  # AJUSTAR SEGÚN TUS VALORES
newOutput = TxOut(output_amount, script_pubkey)

# Crear la transacción
newTx = Tx(1, [input1, input2], [newOutput], 0, True)

# Firmar ambos inputs con privKey1
newTx.sign_input(0, privKey1)
newTx.sign_input(1, privKey1)

# Verificar
print('Transacción válida:', newTx.verify())

# Obtener hex para enviar
print('Hex de transacción:', newTx.serialize().hex())
print('Transaction hash:', newTx.id())
""")

# =============================================================================
# PARTE 3: Transacción P2PKH a P2PKH y P2SH (1 input -> 2 outputs)
# =============================================================================
print("\n" + "="*60)
print("PARTE 3: Transacción P2PKH a P2PKH y P2SH")
print("="*60)

# Generar dirección 3 (P2SH con redeem script = P2PKH de dirección 1)
redeemScript = p2pkh_script_from_address(address1)
h160_redeem = hash160(redeemScript.raw_serialize())

# Crear dirección P2SH (dirección 3)
prefix = b'\xc4'  # testnet P2SH prefix
address3 = encode_base58_checksum(prefix + h160_redeem)

print(f"\nDirección 3 (P2SH):")
print(f"  Redeem Script: {redeemScript}")
print(f"  Hash160 del Redeem Script: {h160_redeem.hex()}")
print(f"  Dirección P2SH: {address3}")

faucet_address = 'mohjSavDdQYHRYXcS3uS6ttaHP8amyvX78'
print(f"\nDirección del Faucet (P2PKH): {faucet_address}")

print("\nEjemplo de código para Parte 3:")
print("""
# CONFIGURAR CON TX HASH DE LA PARTE 2:
tx_hash_parte2 = 'TX_HASH_DE_PARTE_2'
tx_index_parte2 = 0  # usualmente 0

# Crear input
input_parte3 = TxIn(bytes.fromhex(tx_hash_parte2), tx_index_parte2)

# Crear outputs (50% a dirección 3, 50% al faucet)
# Si el output de parte 2 fue 18000 satoshis:
# 50% = 9000, pero deja ~1000 para fee
monto_total = 18000  # AJUSTAR SEGÚN TU VALOR
monto_cada_output = (monto_total - 1000) // 2  # ~8500 cada uno

# Output 1: a dirección 3 (P2SH)
script_p2sh = p2sh_script_from_address(address3)
output1 = TxOut(monto_cada_output, script_p2sh)

# Output 2: al faucet (P2PKH)
script_faucet = p2pkh_script_from_address(faucet_address)
output2 = TxOut(monto_cada_output, script_faucet)

# Crear transacción
newTx3 = Tx(1, [input_parte3], [output1, output2], 0, True)

# Firmar con privKey2 (porque el input viene de dirección 2)
newTx3.sign_input(0, privKey2)

# Verificar
print('Transacción válida:', newTx3.verify())

# Obtener hex
print('Hex de transacción:', newTx3.serialize().hex())
print('Transaction hash:', newTx3.id())
""")

# =============================================================================
# PARTE 4: Transacción P2SH a P2PKH (gastar desde dirección 3)
# =============================================================================
print("\n" + "="*60)
print("PARTE 4: Transacción P2SH a P2PKH")
print("="*60)

print("\nEjemplo de código para Parte 4:")
print("""
# CONFIGURAR CON TX HASH DE LA PARTE 3:
tx_hash_parte3 = 'TX_HASH_DE_PARTE_3'
tx_index_parte3 = 0  # El índice del output que fue a dirección 3

# Crear input
input_parte4 = TxIn(bytes.fromhex(tx_hash_parte3), tx_index_parte3)

# Crear output al faucet
# Si recibiste ~8500 en dirección 3, deja ~500 para fee
monto_p4 = 8000  # AJUSTAR
script_faucet = p2pkh_script_from_address(faucet_address)
output_p4 = TxOut(monto_p4, script_faucet)

# Crear transacción
newTx4 = Tx(1, [input_parte4], [output_p4], 0, True)

# IMPORTANTE: Para P2SH, necesitamos pasar el redeemScript al firmar
# Firmar con privKey1 (porque el redeemScript es P2PKH de dirección 1)
newTx4.sign_input(0, privKey1, redeemScript)

# Verificar
print('Transacción válida:', newTx4.verify(redeemScript))

# Obtener hex
print('Hex de transacción:', newTx4.serialize().hex())
print('Transaction hash:', newTx4.id())
""")

print("\n" + "="*60)
print("RESUMEN DE ENTREGA")
print("="*60)
print("""
PARTE 1:
  - Llave secreta 1 (hex)
  - Dirección 1
  - Llave secreta 2 (hex)  
  - Dirección 2
  - Link a block explorer mostrando 2 transacciones a dirección 1

PARTE 2:
  - Hex de transacción (newTx.serialize().hex())
  - Transaction hash (newTx.id())
  - Verificar en block explorer que fondos llegaron a dirección 2

PARTE 3:
  - Hex de transacción
  - Transaction hash
  - Verificar fondos llegaron a dirección 3 y al faucet

PARTE 4:
  - Hex de transacción
  - Transaction hash
  - Verificar fondos llegaron al faucet
""")

print("\n" + "="*60)
print("IMPORTANTE")
print("="*60)
print("""
1. Reemplaza 'SuNombre' con tu nombre real en las llaves secretas
2. Espera confirmaciones entre transacciones (~10 minutos)
3. Usa block explorer para verificar tx_hash y tx_index correctos
4. Ajusta los montos según lo que realmente recibas
5. Siempre deja espacio para transaction fee (1000-2000 satoshis)
6. Verifica cada transacción con .verify() antes de enviar
7. Usa https://live.blockcypher.com/btc/pushtx/ para enviar (selecciona testnet)
""")
