"use strict";
const btn = document.getElementById('btnReservar');
const btnGetItinerarios = document.getElementById('btnUpdateItinerarios');
const btnCancelar = document.getElementById('btnCancelar');
const resultado = document.getElementById('resultado');
btnGetItinerarios.addEventListener('click', async () => {
    try {
        const res = await fetch('http://localhost:8000/get_itinerarios');
        if (!res.ok)
            throw new Error(`Erro ${res.status}`);
        const data = await res.json();
        // resultado.textContent = JSON.stringify(data, null, 2);
        const tabela = document.getElementById('itinerarios');
        tabela.innerHTML = `
      <tr>
        <th>Código</th>
        <th>Origem</th>
        <th>Destino</th>
        <th>Data</th>
        <th>Noites</th>
      </tr>
      ${data.map((item) => `
        <tr>
          <td>${item.codigo}</td>
          <td>${item.porto_embarque}</td>
          <td>${item.porto_desembarque}</td>
          <td>${item.data}</td>
          <td>${item.numero_noites}</td>
        </tr>
      `).join('')}
    `;
    }
    catch (err) {
        resultado.textContent = `Erro: ${err.message}`;
    }
});
btn.addEventListener('click', async () => {
    try {
        const codigoItinerario = document.getElementById('codigoItinerario').value;
        const res = await fetch(`http://localhost:8000/reservar_passagem?codigo_itinerario=${encodeURIComponent(codigoItinerario)}`);
        if (!res.ok)
            throw new Error(`Erro ${res.status}`);
        const data = await res.json();
        resultado.textContent = JSON.stringify(data, null, 2);
    }
    catch (err) {
        resultado.textContent = `Erro: ${err.message}`;
    }
});
btnCancelar.addEventListener('click', async () => {
    try {
        const codigoItinerario = document.getElementById('codigoItinerario').value;
        const res = await fetch(`http://127.0.0.1:8000/cancelar_reserva?codigo_reserva=${encodeURIComponent(codigoItinerario)}`);
        if (!res.ok)
            throw new Error(`Erro ${res.status}`);
        const data = await res.json();
        resultado.textContent = JSON.stringify(data, null, 2);
    }
    catch (err) {
        resultado.textContent = `Erro: ${err.message}`;
    }
});
