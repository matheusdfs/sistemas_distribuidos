const btn = document.getElementById('btnReservar')!;
const resultado = document.getElementById('resultado')!;

btn.addEventListener('click', async () => {
  try {
    const res = await fetch('http://localhost:8000/reservar_passagem?codigo_itinerario=DPII-01');
    if (!res.ok) throw new Error(`Erro ${res.status}`);
    const data = await res.json();
    resultado.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultado.textContent = `Erro: ${(err as Error).message}`;
  }
});
