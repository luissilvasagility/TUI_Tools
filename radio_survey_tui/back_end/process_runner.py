import socket
import asyncio
import subprocess


HOST = '127.0.0.1'  # Standard loopback interface (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def run_survey_script() -> None:

    running_process = None

    # Set up the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Backend Server listening on {HOST}:{PORT}...")

        while True:
            # Wait for a connection from the client (TUI)
            conn, addr = s.accept()
            with conn:
                # Receive the command (up to 1024 bytes)
                data = conn.recv(1024)
                if not data:
                    continue
                
                command = data.decode('utf-8').strip().lower()
                response = ""
                
                print(command)
                # --- Handle the Commands ---
                if command == 'startdigi':
                    if running_process is None or running_process.poll() is not None:
                        # Start the target script in the background
                        running_process = subprocess.Popen(['bash', '/agility/radio_testing/digi_client/run_digi_receiver_docker.sh'],
                                                           cwd="/agility/radio_testing/digi_client")
                        response = "Process STARTED successfully."
                        print("Command executed: Started process.")
                    else:
                        response = "Process is ALREADY running."

                elif command == 'stopdigi':
                    if running_process is not None and running_process.poll() is None:
                        # Gracefully terminate the process
                        container_ids = subprocess.run(['docker', 'ps', '-q'], capture_output=True, text=True)
                        container_ids = container_ids.stdout.strip().split()
                        subprocess.run(['docker', 'stop'] + container_ids)
                        running_process.terminate()
                        running_process.wait() # Wait for it to actually close
                        response = "Process STOPPED successfully."
                        print("Command executed: Stopped process.")
                    else:
                        response = "Process is NOT running."

                elif command == 'startdoodle':
                    if running_process is None or running_process.poll() is not None:
                        # Start the target script in the background
                        running_process = subprocess.Popen(['bash', '/agility/radio_testing/doodle_labs_client/run_doodle_labs_receiver_docker.sh'],
                                                           cwd="/agility/radio_testing/doodle_labs_client")
                        response = "Process STARTED successfully."
                        print("Command executed: Started process.")
                    else:
                        response = "Process is ALREADY running."

                elif command == 'stopdoodle':
                    if running_process is not None and running_process.poll() is None:
                        # Gracefully terminate the process
                        container_ids = subprocess.run(['docker', 'ps', '-q'], capture_output=True, text=True)
                        container_ids = container_ids.stdout.strip().split()
                        subprocess.run(['docker', 'stop'] + container_ids)
                        running_process.terminate()
                        running_process.wait() # Wait for it to actually close
                        response = "Process STOPPED successfully."
                        print("Command executed: Stopped process.")
                    else:
                        response = "Process is NOT running."
                
                else:
                    response = f"Unknown command: {command}"

                # Send the status back to the client
                conn.sendall(response.encode('utf-8'))

if __name__ == "__main__":
    run_survey_script()
