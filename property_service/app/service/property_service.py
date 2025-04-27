import grpc
from concurrent import futures
import json
from ..proto_files import property_pb2, property_pb2_grpc
from ..repository.property_repository import (
    get_property_by_id, create_property, update_property,
    delete_property, get_user_properties, search_properties,
    get_properties
)

class PropertyService(property_pb2_grpc.PropertyServiceServicer):
    def GetProperty(self, request, context):
        property = get_property_by_id(request.property_id)
        if not property:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Property not found")
            return property_pb2.PropertyResponse()

        # Parse JSON strings back to lists
        images = json.loads(property.images) if property.images else []
        amenities = json.loads(property.amenities) if property.amenities else []

        return property_pb2.PropertyResponse(
            property_id=property.property_id,
            user_id=property.user_id,
            title=property.title,
            description=property.description,
            price=property.price,
            location=property.location,
            property_type=property.property_type,
            status=property.status,
            images=images,
            bedrooms=property.bedrooms,
            bathrooms=property.bathrooms,
            area=property.area,
            year_built=property.year_built,
            amenities=amenities,
            latitude=property.latitude,
            longitude=property.longitude,
            address=property.address,
            city=property.city,
            state=property.state,
            country=property.country,
            zip_code=property.zip_code,
            is_active=property.is_active
        )

    def CreateProperty(self, request, context):
        property_data = {
            'user_id': request.user_id,
            'title': request.title,
            'description': request.description,
            'price': request.price,
            'location': request.location,
            'property_type': request.property_type,
            'status': request.status,
            'images': request.images,
            'bedrooms': request.bedrooms,
            'bathrooms': request.bathrooms,
            'area': request.area,
            'year_built': request.year_built,
            'amenities': request.amenities,
            'latitude': request.latitude,
            'longitude': request.longitude,
            'address': request.address,
            'city': request.city,
            'state': request.state,
            'country': request.country,
            'zip_code': request.zip_code
        }
        
        property_id = create_property(property_data)
        return self.GetProperty(property_pb2.PropertyRequest(property_id=property_id), context)

    def UpdateProperty(self, request, context):
        property_data = {
            'user_id': request.property.user_id,
            'title': request.property.title,
            'description': request.property.description,
            'price': request.property.price,
            'location': request.property.location,
            'property_type': request.property.property_type,
            'status': request.property.status,
            'images': request.property.images,
            'bedrooms': request.property.bedrooms,
            'bathrooms': request.property.bathrooms,
            'area': request.property.area,
            'year_built': request.property.year_built,
            'amenities': request.property.amenities,
            'latitude': request.property.latitude,
            'longitude': request.property.longitude,
            'address': request.property.address,
            'city': request.property.city,
            'state': request.property.state,
            'country': request.property.country,
            'zip_code': request.property.zip_code
        }
        
        success = update_property(request.property_id, property_data)
        if not success:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Property not found")
            return property_pb2.PropertyResponse()
            
        return self.GetProperty(property_pb2.PropertyRequest(property_id=request.property_id), context)

    def DeleteProperty(self, request, context):
        success = delete_property(request.property_id)
        return property_pb2.DeletePropertyResponse(success=success)

    def GetUserProperties(self, request, context):
        properties = get_user_properties(request.user_id)
        return property_pb2.PropertiesResponse(
            properties=[self.GetProperty(property_pb2.PropertyRequest(property_id=p.property_id), context) for p in properties]
        )

    def SearchProperties(self, request, context):
        properties = search_properties(request.query, request.skip, request.limit)
        return property_pb2.PropertiesResponse(
            properties=[self.GetProperty(property_pb2.PropertyRequest(property_id=p.property_id), context) for p in properties]
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    property_pb2_grpc.add_PropertyServiceServicer_to_server(PropertyService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 