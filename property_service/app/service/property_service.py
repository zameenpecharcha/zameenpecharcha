import grpc
from concurrent import futures
from ..proto_files import property_pb2, property_pb2_grpc
from ..repository.property_repository import PropertyRepository
from datetime import datetime

class PropertyService(property_pb2_grpc.PropertyServiceServicer):
    def __init__(self):
        self.repository = PropertyRepository()

    def GetProperty(self, request, context):
        try:
            property_data = self.repository.get_property_by_id(request.id)
            if not property_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")

            return property_pb2.PropertyResponse(
                success=True,
                message="Property retrieved successfully",
                property=self._convert_to_proto_property(property_data)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def CreateProperty(self, request, context):
        try:
            property_data = self._convert_from_proto_property(request)
            created_property = self.repository.create_property(property_data)
            
            return property_pb2.PropertyResponse(
                success=True,
                message="Property created successfully",
                property=self._convert_to_proto_property(created_property)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def UpdateProperty(self, request, context):
        try:
            property_data = self._convert_from_proto_property(request)
            updated_property = self.repository.update_property(request.id, property_data)
            
            if not updated_property:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")

            return property_pb2.PropertyResponse(
                success=True,
                message="Property updated successfully",
                property=self._convert_to_proto_property(updated_property)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def DeleteProperty(self, request, context):
        try:
            success = self.repository.delete_property(request.id)
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")
            
            return property_pb2.PropertyResponse(
                success=True,
                message="Property deleted successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def SearchProperties(self, request, context):
        try:
            properties, total_count = self.repository.search_properties(
                query=request.query,
                property_type=request.property_type,
                listing_type=request.listing_type,
                min_price=request.min_price,
                max_price=request.max_price,
                location=request.location,
                city=request.city,
                state=request.state,
                country=request.country,
                min_bathrooms=request.min_bathrooms,
                min_area=request.min_area,
                max_area=request.max_area,
                construction_status=request.construction_status,
                verification_status=request.verification_status,
                page=request.page if request.page > 0 else 1,
                limit=min(request.limit, 100) if request.limit > 0 else 10
            )

            property_messages = [self._convert_to_proto_property(p) for p in properties]
            total_pages = (total_count + request.limit - 1) // request.limit if request.limit > 0 else 1

            return property_pb2.PropertyListResponse(
                success=True,
                message="Properties found successfully",
                properties=property_messages,
                total_count=total_count,
                page=request.page,
                total_pages=total_pages
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyListResponse(success=False, message=str(e))

    def AddPropertyDocument(self, request, context):
        try:
            document = self.repository.add_property_document(
                property_id=request.property_id,
                doc_name=request.doc_name,
                doc_url=request.doc_url,
                uploaded_by=request.uploaded_by
            )
            
            property_data = self.repository.get_property_by_id(request.property_id)
            return property_pb2.PropertyResponse(
                success=True,
                message="Document added successfully",
                property=self._convert_to_proto_property(property_data)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def AddPropertyFeature(self, request, context):
        try:
            feature = self.repository.add_property_feature(
                property_id=request.property_id,
                feature_name=request.feature_name,
                feature_value=request.feature_value
            )
            
            property_data = self.repository.get_property_by_id(request.property_id)
            return property_pb2.PropertyResponse(
                success=True,
                message="Feature added successfully",
                property=self._convert_to_proto_property(property_data)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def AddMedia(self, request, context):
        try:
            media = self.repository.add_media(
                context_id=request.context_id,
                context_type=request.context_type,
                media_type=request.media_type,
                media_url=request.media_url,
                media_order=request.media_order,
                media_size=request.media_size,
                caption=request.caption
            )
            
            property_data = self.repository.get_property_by_id(request.context_id)
            return property_pb2.PropertyResponse(
                success=True,
                message="Media added successfully",
                property=self._convert_to_proto_property(property_data)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def AddUserProperty(self, request, context):
        try:
            user_property = self.repository.add_user_property(
                user_id=request.user_id,
                property_id=request.property_id,
                role=request.role,
                is_primary=request.is_primary
            )
            
            property_data = self.repository.get_property_by_id(request.property_id)
            return property_pb2.PropertyResponse(
                success=True,
                message="User property relationship added successfully",
                property=self._convert_to_proto_property(property_data)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def VerifyProperty(self, request, context):
        try:
            property_data = self.repository.verify_property(request.id)
            if not property_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")

            return property_pb2.PropertyResponse(
                success=True,
                message="Property verified successfully",
                property=self._convert_to_proto_property(property_data)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def FlagProperty(self, request, context):
        try:
            property_data = self.repository.flag_property(request.id)
            if not property_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")

            return property_pb2.PropertyResponse(
                success=True,
                message="Property flagged successfully",
                property=self._convert_to_proto_property(property_data)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def _convert_to_proto_property(self, db_property):
        """Convert database property object to proto property message"""
        return property_pb2.Property(
            id=db_property.id,
            title=db_property.title,
            builder_name=db_property.builder_name,
            project_name=db_property.project_name,
            rera_id=db_property.rera_id,
            year_build=db_property.year_build,
            no_of_floors=db_property.no_of_floors,
            no_of_units=db_property.no_of_units,
            building_amenities=db_property.building_amenities,
            verification_status=db_property.verification_status,
            verified_by=db_property.verified_by,
            like_count=db_property.like_count,
            is_flagged=db_property.is_flagged,
            average_rating=db_property.average_rating,
            review_count=db_property.review_count,
            description=db_property.description,
            property_type=db_property.property_type,
            listing_type=db_property.listing_type,
            price=db_property.price,
            area_size=db_property.area_size,
            bathroom_count=db_property.bathroom_count,
            construction_status=db_property.construction_status,
            availability_date=int(db_property.availability_date.timestamp()) if db_property.availability_date else 0,
            location=db_property.location,
            city=db_property.city,
            state=db_property.state,
            country=db_property.country,
            pin_code=db_property.pin_code,
            latitude=db_property.latitude,
            longitude=db_property.longitude,
            status=db_property.status,
            created_at=int(db_property.created_at.timestamp()) if db_property.created_at else 0,
            updated_at=int(db_property.updated_at.timestamp()) if db_property.updated_at else 0,
            documents=[self._convert_to_proto_document(d) for d in db_property.documents],
            features=[self._convert_to_proto_feature(f) for f in db_property.features],
            media=[self._convert_to_proto_media(m) for m in db_property.media],
            user_properties=[self._convert_to_proto_user_property(up) for up in db_property.user_properties]
        )

    def _convert_from_proto_property(self, proto_property):
        """Convert proto property message to database property dict"""
        return {
            'title': proto_property.title,
            'builder_name': proto_property.builder_name,
            'project_name': proto_property.project_name,
            'rera_id': proto_property.rera_id,
            'year_build': proto_property.year_build,
            'no_of_floors': proto_property.no_of_floors,
            'no_of_units': proto_property.no_of_units,
            'building_amenities': proto_property.building_amenities,
            'verification_status': proto_property.verification_status,
            'verified_by': proto_property.verified_by,
            'like_count': proto_property.like_count,
            'is_flagged': proto_property.is_flagged,
            'average_rating': proto_property.average_rating,
            'review_count': proto_property.review_count,
            'description': proto_property.description,
            'property_type': proto_property.property_type,
            'listing_type': proto_property.listing_type,
            'price': proto_property.price,
            'area_size': proto_property.area_size,
            'bathroom_count': proto_property.bathroom_count,
            'construction_status': proto_property.construction_status,
            'availability_date': datetime.fromtimestamp(proto_property.availability_date) if proto_property.availability_date else None,
            'location': proto_property.location,
            'city': proto_property.city,
            'state': proto_property.state,
            'country': proto_property.country,
            'pin_code': proto_property.pin_code,
            'latitude': proto_property.latitude,
            'longitude': proto_property.longitude,
            'status': proto_property.status
        }

    def _convert_to_proto_document(self, db_document):
        """Convert database document object to proto document message"""
        return property_pb2.PropertyDocument(
            id=db_document.id,
            property_id=db_document.property_id,
            doc_name=db_document.doc_name,
            doc_url=db_document.doc_url,
            uploaded_by=db_document.uploaded_by,
            is_verified=db_document.is_verified
        )

    def _convert_to_proto_feature(self, db_feature):
        """Convert database feature object to proto feature message"""
        return property_pb2.PropertyFeature(
            id=db_feature.id,
            property_id=db_feature.property_id,
            feature_name=db_feature.feature_name,
            feature_value=db_feature.feature_value
        )

    def _convert_to_proto_media(self, db_media):
        """Convert database media object to proto media message"""
        return property_pb2.Media(
            id=db_media.id,
            context_id=db_media.context_id,
            context_type=db_media.context_type,
            media_type=db_media.media_type,
            media_url=db_media.media_url,
            media_order=db_media.media_order,
            media_size=db_media.media_size,
            caption=db_media.caption,
            uploaded_at=int(db_media.uploaded_at.timestamp()) if db_media.uploaded_at else 0
        )

    def _convert_to_proto_user_property(self, db_user_property):
        """Convert database user_property object to proto user_property message"""
        return property_pb2.UserProperty(
            id=db_user_property.id,
            user_id=db_user_property.user_id,
            property_id=db_user_property.property_id,
            role=db_user_property.role,
            is_primary=db_user_property.is_primary,
            added_at=int(db_user_property.added_at.timestamp()) if db_user_property.added_at else 0
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    property_pb2_grpc.add_PropertyServiceServicer_to_server(PropertyService(), server)
    server.add_insecure_port('[::]:50053')
    print("Starting property service on port 50053...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 