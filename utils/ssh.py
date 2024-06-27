import paramiko
import time
import shlex
import base64
import traceback
import subprocess

# Function to establish an SSH connection
def create_ssh_client(server, port, user, password=None, key_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if key_file:
        print('try to connect')
        client.connect(server, port, user, key_filename=key_file, password=password)
        print('connected')
    else:
        client.connect(server, port, user, password=password)
    return client

# SSH connection details
first_server = {
    'hostname': 'kawung.cs.ui.ac.id',
    'port': 12122,
    'username': 'anindya.sasriya',
    'key_file': '/home/bintangabriel/dgx/anindya.sasriya_kawung.key',
    'password': 'SSEKK'  # Use None if not needed
}

dgx_server = {
    'hostname': '10.119.105.200',
    'username': 'anindyasasriya',
    'password': 'anindyasasriya2024'
}

service_url = 'http://10.233.56.193:80/gpu/'

def tunnel_modeling_dgx(curl_command, file_bytes=None, predict=False):
  try:
    # Step 1: Connect to the first server
    print('req acc')
    first_client = create_ssh_client(
        first_server['hostname'],
        first_server['port'],
        first_server['username'],
        first_server['password'],
        first_server['key_file']
    )

    # Step 2: Create a transport and channel for the second SSH connection
    transport = first_client.get_transport()
    channel = transport.open_channel("direct-tcpip", (dgx_server['hostname'], 22), (first_server["hostname"], 0))
    if channel is not None:
        print('Channel to DGX server opened successfully')
    else:
        print('Failed to open channel to DGX server')

    # Step 3: Connect to the DGX server through the first server
    dgx_client = paramiko.SSHClient()
    dgx_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    dgx_client.connect(dgx_server['hostname'], username=dgx_server['username'], password=dgx_server['password'], sock=channel)
    print('connected to dgx')

    stdin, stdout, stderr = dgx_client.exec_command('echo "Hello, DGX!"')
    hello_output = stdout.read().decode().strip()
    error_output = stderr.read().decode().strip()
    print(f"DGX echo response: {hello_output}")
    if error_output:
        print(f"DGX echo error: {error_output}")

    # Step 4: Execute the curl command on the DGX server
    print('Before exec_command')
    print(curl_command)
    stdin, stdout, stderr = dgx_client.exec_command(curl_command)

    if (file_bytes != None):
        if (predict):
            file_content = file_bytes.read()
            stdin.write(file_content)
            stdin.channel.shutdown_write()
        else:
            stdin.write(file_bytes)
            stdin.channel.shutdown_write()
    
    print('After exec_command')
    response = stdout.read().decode().strip()
    curl_error = stderr.read().decode().strip()

    print(response)
    print(curl_error)
    # Close all connections
    dgx_client.close()
    first_client.close()
    return response
  except paramiko.SSHException as ssh_exception:
    print("SSH connection error:", ssh_exception)
  except Exception as e: 
    print(f"Exception occurred: {str(e)}")
    traceback.print_exc()

def tunnel_modeling_dgx_download(curl_command, file_bytes=None, predict=False):
  try:
    # Step 1: Connect to the first server
    print('req acc')
    first_client = create_ssh_client(
        first_server['hostname'],
        first_server['port'],
        first_server['username'],
        first_server['password'],
        first_server['key_file']
    )

    # Step 2: Create a transport and channel for the second SSH connection
    transport = first_client.get_transport()
    channel = transport.open_channel("direct-tcpip", (dgx_server['hostname'], 22), (first_server["hostname"], 0))
    if channel is not None:
        print('Channel to DGX server opened successfully')
    else:
        print('Failed to open channel to DGX server')

    # Step 3: Connect to the DGX server through the first server
    dgx_client = paramiko.SSHClient()
    dgx_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    dgx_client.connect(dgx_server['hostname'], username=dgx_server['username'], password=dgx_server['password'], sock=channel)
    print('connected to dgx')

    stdin, stdout, stderr = dgx_client.exec_command('echo "Hello, DGX!"')
    hello_output = stdout.read().decode().strip()
    error_output = stderr.read().decode().strip()
    print(f"DGX echo response: {hello_output}")
    if error_output:
        print(f"DGX echo error: {error_output}")

    # Step 4: Execute the curl command on the DGX server
    print('Before exec_command')
    print(curl_command)
    stdin, stdout, stderr = dgx_client.exec_command(curl_command)

    if (file_bytes != None):
        if (predict):
            file_content = file_bytes.read()
            stdin.write(file_content)
            stdin.channel.shutdown_write()
        else:
            stdin.write(file_bytes)
            stdin.channel.shutdown_write()
    
    print('After exec_command')
    response = stdout.read()
    curl_error = stderr.read()

    print('error', curl_error)
    # Close all connections
    dgx_client.close()
    first_client.close()
    return response
  except paramiko.SSHException as ssh_exception:
    print("SSH connection error:", ssh_exception)
  except Exception as e: 
    print(f"Exception occurred: {str(e)}")
    traceback.print_exc()



def gpu_tunneling_checker(curl_command):
    try:
        # Step 1: Connect to the first server
        print('req acc')
        first_client = create_ssh_client(
            first_server['hostname'],
            first_server['port'],
            first_server['username'],
            first_server['password'],
            first_server['key_file']
        )

        # Step 2: Create a transport and channel for the second SSH connection
        transport = first_client.get_transport()
        channel = transport.open_channel("direct-tcpip", (dgx_server['hostname'], 22), (first_server["hostname"], 0))
        if channel is not None:
            print('Channel to DGX server opened successfully')
        else:
            print('Failed to open channel to DGX server')

        # Step 3: Connect to the DGX server through the first server
        dgx_client = paramiko.SSHClient()
        dgx_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        dgx_client.connect(dgx_server['hostname'], username=dgx_server['username'], password=dgx_server['password'], sock=channel)
        print('connected to dgx')

        stdin, stdout, stderr = dgx_client.exec_command('echo "Hello, DGX!"')
        hello_output = stdout.read().decode().strip()
        error_output = stderr.read().decode().strip()
        print(f"DGX echo response: {hello_output}")
        if error_output:
            print(f"DGX echo error: {error_output}")

        # Step 4: Test DNS resolution
        stdin, stdout, stderr = dgx_client.exec_command('nslookup 10.233.13.197')
        nslookup_output = stdout.read().decode().strip()
        nslookup_error = stderr.read().decode().strip()
        print(f"nslookup response: {nslookup_output}")
        if nslookup_error:
            print(f"nslookup error: {nslookup_error}")

        # Step 5: Execute the curl command with verbose output
        print('Before exec_command')
        print(curl_command)
        stdin, stdout, stderr = dgx_client.exec_command(f'curl -v -X GET http://10.233.13.197:8000/gpu/')
        
        print('After exec_command')
        verbose_response = stdout.read().decode().strip()
        verbose_error = stderr.read().decode().strip()
        print('Verbose curl response: ', verbose_response)
        print('Verbose curl error: ', verbose_error)

        # Close all connections
        dgx_client.close()
        first_client.close()
        return verbose_response
    except paramiko.SSHException as ssh_exception:
        print("SSH connection error:", ssh_exception)
    except Exception as e: 
        print(f"Exception occurred: {str(e)}")
        traceback.print_exc()



def generate_curl_command(url, data):
    curl_command = f"curl -s -X POST {shlex.quote(url)}"

    # Add form data
    for key, value in data.items():
        curl_command += f" -F {shlex.quote(f'{key}={value}')}"

    # # Add file
    # curl_command += f" -F {shlex.quote(f'file=@-')}"
    
    return curl_command

def generate_curl_command_without_files(url, data):
    curl_command = f"curl -s -X POST {shlex.quote(url)}"
    
    # Add form data
    for key, value in data.items():
        curl_command += f" -F {shlex.quote(f'{key}={value}')}"
    
    return curl_command


# def test_curl(curl_command, file): 
#     curl_command = [
#     'curl',
#     '-s',  # Silent mode
#     '-X', 'POST',
#     'http://127.0.0.1:7000/train/',
#     '-F', 'model_type=50_deeplab0',
#     '-F', 'model_name=dadada',
#     '-F', 'type=object_segmentation',
#     '-F', 'username=tes',
#     '-F', 'workspace=Workspace 1',
#     '-F', 'filename=carvana_demo (3).zip',
#     '-F', 'gpu=[]',
#     '-F', 'id=37',
#     '-F', 'epoch=4',
#     '-F', 'learning_rate=0.0001',
#     '-F', 'file=@-'
#     ]
#     print('tes')
    
#     try:
#         result = subprocess.run(curl_command, input=file, capture_output=True, check=True)
#         print("Curl command output:", result.stdout)
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         print("Error executing curl command:", e)
#         return None