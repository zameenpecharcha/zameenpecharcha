GRPC Microservice Implementation for User Service.

To generate the protobuffer file need to run the cmd-

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto_files/user.proto

It will generate in the package of proto_files

TO test the grpc service download the bloomrpc tool.
url- https://github.com/bloomrpc/bloomrpc/releases