# src/services/location_service.py
import math
from src.config.settings import ALLOWED_RADIUS_KM, OFFICE_LATITUDE, OFFICE_LONGITUDE
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class LocationService:
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        earth_radius = 6371
        distance = earth_radius * c
        
        return distance

    @staticmethod
    def validate_location(latitude: float, longitude: float) -> dict:
        """
        Validate if the given coordinates are within allowed radius from office
        """
        try:
            # Calculate distance from office
            distance = LocationService.calculate_distance(
                OFFICE_LATITUDE,
                OFFICE_LONGITUDE,
                latitude,
                longitude
            )

            # Check if within allowed radius
            is_valid = distance <= ALLOWED_RADIUS_KM

            if not is_valid:
                raise AppError(
                    400, 
                    MESSAGE_CODE.BAD_REQUEST, 
                    f"Location is too far from office. Distance: {distance:.2f}km (Max allowed: {ALLOWED_RADIUS_KM}km)"
                )

            return {
                "is_valid": True,
                "distance_km": round(distance, 2),
                "max_allowed_km": ALLOWED_RADIUS_KM
            }

        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Location validation failed: {str(e)}")

    @staticmethod
    def get_office_location() -> dict:
        """
        Get office location coordinates
        """
        return {
            "latitude": OFFICE_LATITUDE,
            "longitude": OFFICE_LONGITUDE,
            "radius_km": ALLOWED_RADIUS_KM
        }