"""Formato único de montos de dinero del portafolio (pesos o dólares, convención de Chile).

Todos los scripts que escriben un monto con "$" usan dinero(); ninguno arma el texto a mano (regla R38 del validador).
El signo va antes del "$": -$250, nunca $-250. Separador de miles ".", decimal ",".
El cuaderno de Kaggle no puede importar este archivo: su primera celda de código define una copia de dinero()
y el validador comprueba que ambas den el mismo resultado.
"""
from __future__ import annotations


def dinero(v, dec: int = 0) -> str:
    """Monto con signo delante del "$", miles con punto y decimales con coma: dinero(-250) == "-$250"."""
    v = float(v)
    if dec == 0:
        n = int(round(abs(v)))
        cuerpo = f"{n:,}".replace(",", ".")
        cero = n == 0
    else:
        cuerpo = f"{abs(v):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        cero = cuerpo.strip("0,.") == ""
    signo = "-" if v < 0 and not cero else ""
    return f"{signo}${cuerpo}"
