from grpc_tools import protoc
import os

def generate_proto():
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    proto_dir = os.path.join(current_dir, 'app', 'proto_files')
    
    # Generate the gRPC files
    command = [
        'grpc_tools.protoc',
        f'--proto_path={proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        '--experimental_allow_proto3_optional',  # For optional fields
        os.path.join(proto_dir, 'user.proto')
    ]
    
    print(f"Generating gRPC code from {os.path.join(proto_dir, 'user.proto')}...")
    protoc.main(command)
    
    # Fix imports in generated files
    grpc_file = os.path.join(proto_dir, 'user_pb2_grpc.py')
    with open(grpc_file, 'r') as f:
        content = f.read()
    
    # Fix the import
    content = content.replace(
        'import user_pb2 as user__pb2',
        'from . import user_pb2 as user__pb2'
    )
    
    with open(grpc_file, 'w') as f:
        f.write(content)
    
    print("Proto files generated successfully!")

if __name__ == '__main__':
    generate_proto()