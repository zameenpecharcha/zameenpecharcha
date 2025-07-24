import os
import sys
from grpc_tools import protoc

def generate_proto():
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    proto_dir = os.path.join(current_dir, 'app', 'proto_files')
    
    # Generate main service protos
    post_proto = os.path.join(proto_dir, 'post.proto')
    generate_single_proto(post_proto, proto_dir)
    
    # Generate external protos
    external_dir = os.path.join(proto_dir, 'external')
    user_proto = os.path.join(external_dir, 'user.proto')
    generate_single_proto(user_proto, external_dir)
    
    print("All proto files generated successfully!")

def generate_single_proto(proto_file: str, proto_dir: str):
    print(f"Generating gRPC code from {proto_file}...")
    command = [
        'grpc_tools.protoc',
        f'--proto_path={proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        proto_file
    ]
    protoc.main(command)

if __name__ == "__main__":
    generate_proto() 