import simpy
import random
import statistics
import matplotlib.pyplot as plt

# PARÁMETROS GENERALES

RANDOM_SEED = 42
PROCESOS = [25, 50, 100, 150, 200]

random.seed(RANDOM_SEED)

# FUNCIÓN PRINCIPAL DE SIMULACIÓN
def simulacion(total_procesos, intervalo, ram_cap, cpu_speed, cpu_count=1):

    tiempos = []

    def proceso(env, RAM, CPU):
        llegada = env.now
        memoria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)

        # NEW → solicitar RAM
        yield RAM.get(memoria)

        while instrucciones > 0:

            # READY → solicitar CPU
            with CPU.request() as req:
                yield req

                # RUNNING
                ejecutar = min(cpu_speed, instrucciones)
                yield env.timeout(1)
                instrucciones -= ejecutar

            # Decidir siguiente estado
            if instrucciones > 0:
                evento = random.randint(1, 21)
                if evento == 1:
                    # WAITING (I/O)
                    yield env.timeout(1)

        # TERMINATED
        RAM.put(memoria)
        tiempos.append(env.now - llegada)

    def generador(env, RAM, CPU):
        for _ in range(total_procesos):
            yield env.timeout(random.expovariate(1.0 / intervalo))
            env.process(proceso(env, RAM, CPU))

    env = simpy.Environment()
    RAM = simpy.Container(env, init=ram_cap, capacity=ram_cap)
    CPU = simpy.Resource(env, capacity=cpu_count)

    env.process(generador(env, RAM, CPU))
    env.run()

    return statistics.mean(tiempos), statistics.stdev(tiempos)


# =========================
# FUNCIÓN PARA EJECUTAR ESCENARIOS Y GRAFICAR
# =========================

def ejecutar_escenario(nombre, intervalo, ram_cap, cpu_speed, cpu_count=1):

    print(f"\n===== {nombre} =====")

    promedios = []

    for p in PROCESOS:
        promedio, desviacion = simulacion(p, intervalo, ram_cap, cpu_speed, cpu_count)
        print(f"Procesos: {p}")
        print(f"Promedio: {promedio:.2f}")
        print(f"Desviación: {desviacion:.2f}")
        print("-----")
        promedios.append(promedio)

    # Graficar
    plt.figure()
    plt.plot(PROCESOS, promedios, marker='o')
    plt.xlabel("Número de procesos")
    plt.ylabel("Tiempo promedio en sistema")
    plt.title(nombre)
    plt.grid()
    plt.savefig(f"{nombre}.png")
    plt.close()


# Escenarios base
ejecutar_escenario("Intervalo_10", 10, 100, 3)
ejecutar_escenario("Intervalo_5", 5, 100, 3)
ejecutar_escenario("Intervalo_1", 1, 100, 3)

# Estrategias de mejora
ejecutar_escenario("RAM_200", 1, 200, 3)
ejecutar_escenario("CPU_6", 1, 100, 6)
ejecutar_escenario("CPU_2", 1, 100, 3, cpu_count=2)

print("\nSimulación completada. Gráficas guardadas correctamente.")