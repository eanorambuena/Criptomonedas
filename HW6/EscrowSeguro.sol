// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EscrowSeguro {

    // --- STATE VARIABLES ---
    address public comprador;
    address payable public vendedor;
    address public arbitro;
    uint public monto;
    
    // Evita ataques de reentrancy (como un semáforo)
    bool internal locked;

    enum Estado { CREADO, PAGADO, ENTREGADO, REEMBOLSADO }
    Estado public estadoActual;

    // Eventos para loguear actividad (útil para el frontend/logs)
    event DepositoRealizado(address quien, uint cuanto);
    event PagoLiberado(address vendedor, uint cuanto);
    event ReembolsoRealizado(address comprador, uint cuanto);

    constructor(address payable _vendedor, address _comprador) {
        arbitro = msg.sender; 
        vendedor = _vendedor;
        comprador = _comprador;
        estadoActual = Estado.CREADO;
        locked = false;
    }

    // --- MODIFIERS ---
    
    // Protección contra Reentrancy (El fix que pide Remix AI)
    modifier noReentrancy() {
        require(!locked, "No re-entrancy allowed");
        locked = true;
        _;
        locked = false;
    }

    modifier soloComprador() {
        require(msg.sender == comprador, "Solo el comprador puede ejecutar esto");
        _;
    }

    modifier soloArbitro() {
        require(msg.sender == arbitro, "Solo el arbitro puede ejecutar esto");
        _;
    }

    modifier enEstado(Estado _estado) {
        require(estadoActual == _estado, "Estado invalido");
        _;
    }

    // --- FUNCIONES ---

    // 1. DEPOSITAR (Payable)
    function depositar() external payable soloComprador enEstado(Estado.CREADO) {
        require(msg.value > 0, "Monto debe ser mayor a 0");
        monto = msg.value;
        estadoActual = Estado.PAGADO;
        emit DepositoRealizado(msg.sender, msg.value);
    }

    // 2. LIBERAR PAGO (Fix: Usando 'call' en lugar de 'transfer')
    function confirmarEntrega() external soloComprador enEstado(Estado.PAGADO) noReentrancy {
        estadoActual = Estado.ENTREGADO;
        
        // Forma segura recomendada actualmente para enviar ETH
        (bool success, ) = vendedor.call{value: address(this).balance}("");
        require(success, "Fallo la transferencia al vendedor");
        
        emit PagoLiberado(vendedor, monto);
    }

    // 3. REEMBOLSAR (Fix: Dándole poder al árbitro para destrabar fondos)
    // Si el vendedor no cumple, el árbitro devuelve la plata al comprador
    function reembolsar() external soloArbitro enEstado(Estado.PAGADO) noReentrancy {
        estadoActual = Estado.REEMBOLSADO;
        
        (bool success, ) = payable(comprador).call{value: address(this).balance}("");
        require(success, "Fallo el reembolso al comprador");

        emit ReembolsoRealizado(comprador, monto);
    }
    
    // View para ver saldo
    function obtenerBalance() external view returns (uint) {
        return address(this).balance;
    }
}
