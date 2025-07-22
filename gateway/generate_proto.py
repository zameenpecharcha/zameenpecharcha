import os
import subprocess

def generate_proto_files():
    # Generate comments proto files
    comments_proto_path = os.path.join('app', 'proto_files', 'comments', 'comments.proto')
    comments_output_path = os.path.join('app', 'proto_files', 'comments')
    
    # Create directory if it doesn't exist
    os.makedirs(comments_output_path, exist_ok=True)
    
    # Create __init__.py files
    init_files = [
        os.path.join('app', 'proto_files', '__init__.py'),
        os.path.join('app', 'proto_files', 'comments', '__init__.py')
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# This file makes the directory a Python package\n')
    
    # Generate Python files from proto
    cmd = [
        'python', '-m', 'grpc_tools.protoc',
        '-I.',
        '--python_out=.',
        '--grpc_python_out=.',
        comments_proto_path
    ]
    
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    generate_proto_files() 