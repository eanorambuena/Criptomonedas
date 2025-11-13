# Tarea 4 - Punto 2: Explicación del Error de Validación

Al intentar validar las transacciones de los bloques descargados, el programa falla con un `ValueError` al procesar la primera transacción de un bloque (la transacción "coinbase").

El *traceback* del error es el siguiente:

```
ValueError: unexpected response: 0000000000000000000000000000000000000000000000000000000000000000 not found
```

Este error es el comportamiento esperado y se produce debido a que el script de validación (`txP2PKH.py`) no está diseñado para manejar el caso especial de las transacciones coinbase.

## Análisis del Fallo

1.  **Qué es una Transacción Coinbase:** La primera transacción en cada bloque (índice 0) es la **transacción coinbase**. Esta transacción no gasta outputs anteriores (UTXOs), sino que *crea* nuevas monedas (la recompensa del bloque) y las asigna al minero.

2.  **Cómo Falla `tx.verify()`:** El proceso de validación en el código sigue estos pasos:

      * Se llama a `coinbase_tx.verify()`.
      * Este método, para asegurar que no se está creando dinero, llama a `self.fee()`.
      * `self.fee()` necesita calcular el valor de los *inputs* de la transacción. Para ello, itera sobre cada `tx_in` y llama a `tx_in.value()`.
      * `tx_in.value()` llama a `TxFetcher.fetch(self.prev_tx.hex())` para buscar la transacción anterior y ver cuánto valía el output que se está gastando.

3.  **La Causa Raíz:**

      * Por convención, un input de una transacción coinbase tiene un `prev_tx` (hash de transacción previa) nulo: `00000000...0000`.
      * El código pasa este hash nulo a `TxFetcher`.
      * El `TxFetcher` realiza una petición HTTP al nodo (ej. `testnet.programmingbitcoin.com`) pidiendo la transacción `00000000...0000`.
      * El servidor responde (correctamente) que esa transacción no existe, devolviendo el *texto* `"0000...0000 not found"`.
      * El `TxFetcher` recibe este texto, asume que es una respuesta *hexadecimal* válida, e intenta parsearla con `bytes.fromhex()`.
      * Esto falla con un `ValueError` porque la cadena de texto `"not found"` no es hexadecimal.

**En conclusión:** El código de validación falla porque asume que todas las transacciones son transacciones de gasto normales. No tiene la lógica necesaria para identificar y omitir la validación de los inputs de una transacción coinbase, que no gasta UTXOs y, por lo tanto, no tiene transacciones previas que buscar.
