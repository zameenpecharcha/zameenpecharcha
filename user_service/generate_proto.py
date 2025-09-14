from grpc_tools import protoc
import os

def generate_proto():
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Proto file path
    proto_file = os.path.join(current_dir, 'app', 'proto_files', 'user.proto')
    proto_dir = os.path.dirname(proto_file)
    
    # Generate the gRPC files
    command = [
        'grpc_tools.protoc',
        f'--proto_path={proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        proto_file
    ]
    
    print(f"Generating gRPC code from {proto_file}...")
    protoc.main(command)
    print("Proto files generated successfully!")

if __name__ == '__main__':
    generate_proto() 