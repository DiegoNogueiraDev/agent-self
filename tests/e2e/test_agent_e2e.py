import unittest
import subprocess
import time
import psutil
import os
from pathlib import Path

# Script 'bomba' que consome memória
MEMORY_BOMB_SCRIPT = """
import time
import sys

megabytes_to_allocate = int(sys.argv[1]) if len(sys.argv) > 1 else 150
print(f"MemoryBomb: Allocating {{megabytes_to_allocate}} MB of memory...")
large_list = ['A' * 1024 * 1024] * megabytes_to_allocate
print("MemoryBomb: Memory allocated. Now looping forever...")
while True:
    time.sleep(1)
"""

AGENT_MAIN_SCRIPT = Path("src/main.py").resolve()
BOMB_SCRIPT_PATH = Path("tests/e2e/memory_bomb.py").resolve()

class TestAgentE2E(unittest.TestCase):

    def setUp(self):
        """Prepara o ambiente de teste E2E."""
        # Cria o script 'bomba'
        with open(BOMB_SCRIPT_PATH, "w") as f:
            f.write(MEMORY_BOMB_SCRIPT)
        
        # Garante que nenhum processo do agente ou bomba esteja rodando
        self._cleanup_processes()

    def tearDown(self):
        """Limpa o ambiente após o teste."""
        self._cleanup_processes()
        # Remove o script 'bomba'
        if os.path.exists(BOMB_SCRIPT_PATH):
            os.remove(BOMB_SCRIPT_PATH)

    def _cleanup_processes(self):
        """Garante que processos de testes anteriores sejam finalizados."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline') or [])
                is_agent = str(AGENT_MAIN_SCRIPT) in cmdline
                is_bomb = str(BOMB_SCRIPT_PATH) in cmdline
                
                if is_agent or is_bomb:
                    print(f"Cleanup: Terminating dangling process {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except psutil.TimeoutExpired:
                proc.kill()


    def test_agent_detects_and_remediates_memory_bomb(self):
        """
        Teste E2E: Inicia um processo que consome muita memória e verifica se o agente o finaliza.
        """
        bomb_process = None
        agent_process = None
        
        try:
            # 1. Inicia o processo 'bomba' de memória
            bomb_process = subprocess.Popen(["python3", str(BOMB_SCRIPT_PATH), "200"]) # Aloca 200MB
            self.assertIsNotNone(bomb_process.pid, "Falha ao iniciar o processo 'bomba' de memória.")
            print(f"Started memory bomb process with PID: {bomb_process.pid}")
            time.sleep(2) # Dá tempo para o processo alocar memória

            # Verifica se a bomba está rodando
            self.assertTrue(psutil.pid_exists(bomb_process.pid), "Processo bomba não está rodando após o início.")

            # 2. Inicia o Agente de Auto-Recuperação
            agent_process = subprocess.Popen(
                ["python3", str(AGENT_MAIN_SCRIPT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.assertIsNotNone(agent_process.pid, "Falha ao iniciar o agente.")
            print(f"Started agent process with PID: {agent_process.pid}")

            # 3. Aguarda o agente agir (ciclos de coleta + remediação)
            # O agente deve detectar e matar a bomba. Damos um tempo generoso.
            max_wait_time = 30  # segundos
            bomb_terminated = False
            end_time = time.time() + max_wait_time

            while time.time() < end_time:
                if bomb_process.poll() is not None: # Processo terminou
                    bomb_terminated = True
                    break
                time.sleep(1)

            # 4. Verifica se o processo 'bomba' foi finalizado
            self.assertTrue(bomb_terminated, 
                f"O agente falhou em finalizar o processo 'bomba' (PID: {bomb_process.pid}) dentro de {max_wait_time} segundos.")
            
            print(f"Success: Agent terminated memory bomb process (PID: {bomb_process.pid}).")
            
            # Opcional: Verificar logs do agente para a ação de remediação
            stdout, stderr = agent_process.communicate(timeout=5)
            self.assertIn("kill_process_by_pid", stdout, "A ação de matar o processo não foi logada na saída do agente.")
            
        finally:
            # Garante que todos os processos sejam finalizados
            if agent_process and agent_process.poll() is None:
                agent_process.terminate()
            if bomb_process and bomb_process.poll() is None:
                bomb_process.terminate()

if __name__ == '__main__':
    unittest.main() 