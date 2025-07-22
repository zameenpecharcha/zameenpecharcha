import os
import subprocess

def generate_proto_files():
    proto_dir = os.path.join('app', 'proto_files')
    posts_dir = os.path.join(proto_dir, 'posts')
    
    # Create posts directory if it doesn't exist
    os.makedirs(posts_dir, exist_ok=True)
    
    # Generate Python files from proto
    cmd = [
        'python', '-m', 'grpc_tools.protoc',
        f'-I{proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        os.path.join(posts_dir, 'post.proto')
    ]
    
    subprocess.run(cmd, check=True)
    
    # Create __init__.py files if they don't exist
    init_files = [
        os.path.join(proto_dir, '__init__.py'),
        os.path.join(posts_dir, '__init__.py')
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# This file makes the directory a Python package\n')

if __name__ == '__main__':
    generate_proto_files() 