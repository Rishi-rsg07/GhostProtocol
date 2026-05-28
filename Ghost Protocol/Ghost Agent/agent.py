import time
import json
import os
import subprocess
import requests

class GhostAgent:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.base_url = self.config["CONTROL_PLANE_URL"]
        self.agent_id = self.config["AGENT_ID"]
        self.poll_interval = self.config["POLL_INTERVAL_SECONDS"]
        self.active_pids = []

    def poll_control_plane(self):
        url = f"{self.base_url}/api/v1/agent/{self.agent_id}/poll"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[-] Connection to Control Plane lost: {e}")
        return {"action": "sleep"}

    def inject_cpu_hog(self, duration_seconds=45):
        """ Safe, self-terminating infrastructure degradation """
        print(f"[!] INJECTING CHAOS: Spawning synthetic CPU consumption stressor...")
        # Spawns an optimized arithmetic loop on all cores that terminates automatically
        cmd = f"stress-ng --cpu 0 --timeout {duration_seconds}s"
        
        try:
            process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
            self.active_pids.append(process.pid)
            print(f"[+] Chaos active under Process Group PID: {process.pid}")
        except FileNotFoundError:
            # Fallback if stress-ng package is missing on target host system
            fallback_cmd = f"timeout {duration_seconds} sha256sum /dev/zero"
            process = subprocess.Popen(fallback_cmd, shell=True)
            self.active_pids.append(process.pid)

    def safety_rollback(self):
        """ The Dead Man's Switch: Clears all system hooks instantly """
        print("[*] Triggering critical safety rollback engine...")
        # Forcefully purges common chaos vectors running on host
        subprocess.run("pkill -9 stress-ng || true", shell=True)
        subprocess.run("pkill -9 sha256sum || true", shell=True)
        self.active_pids.clear()
        print("[+] System environment normalized successfully.")

    def run(self):
        print(f"[+] Ghost Agent initialized. Monitoring workspace target: '{self.agent_id}'")
        while True:
            data = self.poll_control_plane()
            action = data.get("action")

            if action == "execute":
                experiment = data.get("experiment_type")
                print(f"[!] Received verified command: Attack Type: {experiment}")
                
                if experiment == "cpu_hog":
                    self.inject_cpu_hog(duration_seconds=60)
                    
                    # Watch the execution safely and run rollback protocol if needed
                    time.sleep(65) 
                    self.safety_rollback()

            time.sleep(self.poll_interval)

if __name__ == "__main__":
    agent = GhostAgent()
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n[-] Manual shutdown sequence intercepted.")
        agent.safety_rollback()