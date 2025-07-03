import time
import math
import multiprocessing

def stress():
    """Função que executa um loop para consumir CPU."""
    print(f"Iniciando processo de estresse no PID: {multiprocessing.current_process().pid}")
    try:
        while True:
            _ = [math.sqrt(i) for i in range(100000)]
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass

def main():
    """Função principal para iniciar o teste de estresse."""
    cpu_count = multiprocessing.cpu_count()
    print(f"Iniciando teste de estresse da CPU em {cpu_count} núcleo(s). Pressione Ctrl+C para parar.")
    
    processes = []
    for _ in range(cpu_count):
        p = multiprocessing.Process(target=stress)
        p.start()
        processes.append(p)
        
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nParando o teste de estresse da CPU...")
        for p in processes:
            p.terminate()
            p.join()
        print("Teste finalizado.")

if __name__ == "__main__":
    main() 