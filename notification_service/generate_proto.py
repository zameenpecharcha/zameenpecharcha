import os
import subprocess
import sys

def generate_proto_files():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    proto_dir = os.path.join(current_dir, "app", "proto_files")
    output_dir = os.path.join(current_dir, "app", "proto_files")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all proto files
    proto_files = [f for f in os.listdir(proto_dir) if f.endswith('.proto')]
    
    for proto_file in proto_files:
        proto_path = os.path.join(proto_dir, proto_file)
        
        # Generate Python files from proto
        subprocess.run([
            sys.executable, "-m", "grpc_tools.protoc",
            f"--proto_path={proto_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            proto_file
        ], check=True)
        
        print(f"Generated Python files for {proto_file}")

if __name__ == "__main__":
    generate_proto_files() 