import os
import subprocess
import sys

def generate_proto():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Auth service protos
    auth_proto_dir = os.path.join(current_dir, "app", "proto_files", "auth")
    auth_proto_file = os.path.join(auth_proto_dir, "auth.proto")
    
    # Create __init__.py files
    os.makedirs(auth_proto_dir, exist_ok=True)
    with open(os.path.join(auth_proto_dir, "__init__.py"), "w") as f:
        pass
    
    # Command to generate Python code from proto file
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"--proto_path={os.path.dirname(auth_proto_file)}",
        f"--python_out={os.path.dirname(auth_proto_file)}",
        f"--grpc_python_out={os.path.dirname(auth_proto_file)}",
        auth_proto_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Proto files generated successfully!")
        
        # Fix imports in generated files
        pb2_grpc_file = os.path.join(auth_proto_dir, "auth_pb2_grpc.py")
        with open(pb2_grpc_file, 'r') as f:
            content = f.read()
        
        # Replace the import statement
        content = content.replace(
            'import auth_pb2 as auth__pb2',
            'from app.proto_files.auth import auth_pb2 as auth__pb2'
        )
        
        with open(pb2_grpc_file, 'w') as f:
            f.write(content)
            
        print("Fixed imports in generated files!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating proto files: {str(e)}")

if __name__ == "__main__":
    generate_proto() 