"""Practica #04 - Grafo dirigido y ponderado para buscar vuelos baratos.
Estructura: lista de adyacencia (dict de listas). Algoritmos: Dijkstra (heapq) y BFS.
"""
import heapq, random, sys, time
from collections import deque, namedtuple

Vuelo = namedtuple("Vuelo", "origen destino precio duracion aerolinea")


class GrafoVuelos:
    def __init__(self):
        self.ady = {}  # aeropuerto -> lista de Vuelo salientes

    def agregar_vuelo(self, v):
        self.ady.setdefault(v.origen, []).append(v)
        self.ady.setdefault(v.destino, [])

    @classmethod
    def desde_archivo(cls, ruta):
        g = cls()
        with open(ruta, encoding="utf-8") as f:
            for n, linea in enumerate(f, 1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                try:
                    o, d, p, t, a = [x.strip() for x in linea.split(",")]
                    g.agregar_vuelo(Vuelo(o.upper(), d.upper(), float(p), int(t), a))
                except ValueError:
                    print(f"[aviso] linea {n} invalida, se omite: {linea}")
        return g

    # ---------- reporteria ----------
    def num_vuelos(self):
        return sum(len(v) for v in self.ady.values())

    def reporte_estructura(self):
        print(f"Aeropuertos (nodos): {len(self.ady)} | Vuelos (aristas): {self.num_vuelos()}")
        print(f"{'ORIGEN':<7}{'GRADO':<6}DESTINOS (precio USD)")
        for o in sorted(self.ady):
            dest = ", ".join(f"{v.destino}(${v.precio:.0f})" for v in self.ady[o])
            print(f"{o:<7}{len(self.ady[o]):<6}{dest}")

    def vuelos_desde(self, origen):
        origen = origen.upper()
        if origen not in self.ady:
            print("Aeropuerto no existe"); return
        print(f"Vuelos directos desde {origen}:")
        for v in sorted(self.ady[origen], key=lambda x: x.precio):
            print(f"  -> {v.destino}  ${v.precio:.0f}  {v.duracion} min  {v.aerolinea}")

    # ---------- algoritmos ----------
    def ruta_mas_barata(self, origen, destino, criterio="precio"):
        """Dijkstra. criterio: 'precio' o 'duracion'. O((V+E) log V)."""
        origen, destino = origen.upper(), destino.upper()
        if origen not in self.ady or destino not in self.ady:
            return None
        dist = {n: float("inf") for n in self.ady}
        previo = {}
        dist[origen] = 0
        cola = [(0, origen)]
        while cola:
            d, u = heapq.heappop(cola)
            if d > dist[u]:
                continue
            if u == destino:
                break
            for v in self.ady[u]:
                peso = v.precio if criterio == "precio" else v.duracion
                nd = d + peso
                if nd < dist[v.destino]:
                    dist[v.destino] = nd
                    previo[v.destino] = v
                    heapq.heappush(cola, (nd, v.destino))
        if dist[destino] == float("inf"):
            return None
        tramos, n = [], destino
        while n != origen:
            tramos.append(previo[n]); n = previo[n].origen
        return dist[destino], tramos[::-1]

    def ruta_menos_escalas(self, origen, destino):
        """BFS: minimo numero de vuelos. O(V+E)."""
        origen, destino = origen.upper(), destino.upper()
        if origen not in self.ady or destino not in self.ady:
            return None
        prev, vistos, cola = {}, {origen}, deque([origen])
        while cola:
            u = cola.popleft()
            if u == destino:
                break
            for v in self.ady[u]:
                if v.destino not in vistos:
                    vistos.add(v.destino); prev[v.destino] = v; cola.append(v.destino)
        if destino not in vistos:
            return None
        tramos, n = [], destino
        while n != origen:
            tramos.append(prev[n]); n = prev[n].origen
        return tramos[::-1]

    def alcanzables(self, origen):
        """Destinos alcanzables (BFS)."""
        origen = origen.upper(); vistos, cola = {origen}, deque([origen])
        while cola:
            u = cola.popleft()
            for v in self.ady[u]:
                if v.destino not in vistos:
                    vistos.add(v.destino); cola.append(v.destino)
        return sorted(vistos - {origen})


def imprimir_ruta(titulo, tramos):
    if not tramos:
        print(f"{titulo}: sin ruta disponible"); return
    precio = sum(t.precio for t in tramos); mins = sum(t.duracion for t in tramos)
    cam = tramos[0].origen + "".join(f" -> {t.destino}" for t in tramos)
    print(f"{titulo}: {cam}")
    for t in tramos:
        print(f"    {t.origen}->{t.destino}  ${t.precio:.0f}  {t.duracion} min  {t.aerolinea}")
    print(f"    TOTAL: ${precio:.0f} | {mins // 60} h {mins % 60} min | escalas: {len(tramos) - 1}")


def benchmark():
    print("\n=== Analisis de tiempo de ejecucion (Dijkstra, grafos aleatorios) ===")
    print(f"{'V':>8}{'E':>9}{'tiempo (ms)':>14}")
    random.seed(7)
    for n in (100, 1000, 5000, 20000):
        g = GrafoVuelos(); m = n * 5
        for i in range(n):
            g.ady.setdefault(f"N{i}", [])
        for _ in range(m):
            a, b = random.randrange(n), random.randrange(n)
            if a != b:
                g.agregar_vuelo(Vuelo(f"N{a}", f"N{b}", random.randint(30, 600), 60, "X"))
        t = []
        for _ in range(5):
            t0 = time.perf_counter(); g.ruta_mas_barata("N0", f"N{n - 1}"); t.append(time.perf_counter() - t0)
        print(f"{n:>8}{g.num_vuelos():>9}{sum(t) / len(t) * 1000:>14.3f}")


def menu(g):
    while True:
        print("\n1) Reporte del grafo  2) Vuelos desde un aeropuerto  3) Ruta mas barata"
              "\n4) Ruta mas rapida  5) Menos escalas  6) Alcanzables  7) Benchmark  0) Salir")
        op = input("Opcion: ").strip()
        if op == "0": break
        if op == "1": g.reporte_estructura()
        elif op == "7": benchmark()
        elif op in "23456":
            o = input("Origen (ej. ESM): ")
            if op == "2": g.vuelos_desde(o)
            elif op == "6": print("Alcanzables:", ", ".join(g.alcanzables(o)))
            else:
                d = input("Destino (ej. MAD): ")
                if op == "3":
                    r = g.ruta_mas_barata(o, d); imprimir_ruta("Mas barata", r[1] if r else None)
                elif op == "4":
                    r = g.ruta_mas_barata(o, d, "duracion"); imprimir_ruta("Mas rapida", r[1] if r else None)
                else: imprimir_ruta("Menos escalas", g.ruta_menos_escalas(o, d))


if __name__ == "__main__":
    g = GrafoVuelos.desde_archivo("vuelos.txt")
    if "--demo" in sys.argv:
        g.reporte_estructura(); print()
        g.vuelos_desde("ESM"); print()
        for o, d in (("ESM", "MAD"), ("GPS", "MIA"), ("GYE", "UIO")):
            r = g.ruta_mas_barata(o, d); imprimir_ruta(f"Mas barata {o}-{d}", r[1] if r else None)
        r = g.ruta_mas_barata("ESM", "MAD", "duracion"); imprimir_ruta("Mas rapida ESM-MAD", r[1])
        imprimir_ruta("Menos escalas ESM-MAD", g.ruta_menos_escalas("ESM", "MAD"))
        print("Alcanzables desde ESM:", ", ".join(g.alcanzables("ESM")))
        benchmark()
    else:
        menu(g)
