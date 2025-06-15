import os
import subprocess

def generate_proto():
    proto_file = "app/proto_files/feed.proto"
    output_dir = "app/proto_files"
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate Python files from proto
    subprocess.run([
        "python", "-m", "grpc_tools.protoc",
        f"--proto_path=.",
        f"--python_out=.",
        f"--grpc_python_out=.",
        proto_file
    ])

if __name__ == "__main__":
    generate_proto() 