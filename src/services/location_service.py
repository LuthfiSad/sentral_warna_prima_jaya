# src/services/location_service.py
from datetime import time
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
    def _detect_fake_gps(position_data: dict) -> bool:
        """
        Detects potential fake GPS usage based on provided position data.
        This function mirrors the logic from the frontend, adapted for Python.
        """
        coords = position_data.get('coords', {})
        
        # Default values for optional fields if not provided
        accuracy = coords.get('accuracy', 0.0) # Use 0.0 as default if not present
        latitude = coords.get('latitude', 0.0)
        longitude = coords.get('longitude', 0.0)
        altitude = coords.get('altitude') # Can be None
        speed = coords.get('speed')     # Can be None
        heading = coords.get('heading')   # Can be None
        
        # Timestamp from frontend is usually in milliseconds
        # Convert to seconds for Python's time.time() comparison if necessary
        # Or compare directly in milliseconds if all timestamps are milliseconds
        timestamp_ms = position_data.get('timestamp') 
        
        # 1. Cek accuracy yang terlalu sempurna atau sangat rendah
        if accuracy == 0 or accuracy < 3:
            return True

        # 2. Cek koordinat yang terlalu presisi
        lat_str = str(latitude)
        lng_str = str(longitude)

        # Check for more than 7 decimal places or specific repeating patterns
        if (('.' in lat_str and len(lat_str.split('.')[1]) > 7) or
            ('.' in lng_str and len(lng_str.split('.')[1]) > 7) or
            ('.' in lat_str and len(lat_str.split('.')[1]) > 5 and (lat_str.endswith("0000") or lat_str.endswith("9999"))) or
            ('.' in lng_str and len(lng_str.split('.')[1]) > 5 and (lng_str.endswith("0000") or lng_str.endswith("9999")))):
            return True

        # 3. Cek jika altitude terlalu sempurna
        if altitude is not None and altitude != 0 and altitude % 1 == 0 and accuracy < 10:
            return True

        # 4. Cek jika speed dan heading tersedia tapi nilainya 0 (tidak realistis saat berpindah)
        if speed is not None and heading is not None and speed == 0 and heading == 0 and accuracy < 20:
            return True

        # 5. Cek timestamp yang tidak wajar
        if timestamp_ms is not None:
            now_ms = int(time.time() * 1000) # Current time in milliseconds
            time_diff = abs(now_ms - timestamp_ms)

            # Jika timestamp terlalu jauh dari waktu sekarang (lebih dari 60 detik = 60000 ms)
            # Atau jika timestamp di masa depan (lebih dari 5 detik ke depan = 5000 ms)
            if time_diff > 60000 or (timestamp_ms - now_ms > 5000):
                return True
        else:
            # If timestamp is missing, it's suspicious
            return True 

        # 6. Mock location API check is typically not available on the backend
        # unless you integrate with a mobile SDK/service that provides this info.

        return False

    @staticmethod
    def validate_location(latitude: float, longitude: float, position_data: dict = None) -> dict:
        """
        Validate location including fake GPS detection and distance from office.
        `position_data` should contain full GeolocationPosition details from frontend.
        """
        try:
            # 1. Cek koordinat nol (validasi dasar, penting di backend juga)
            if latitude == 0 and longitude == 0:
                raise AppError(
                    400,
                    MESSAGE_CODE.BAD_REQUEST,
                    "Koordinat tidak valid (0,0). Pastikan GPS aktif dengan benar atau coba lagi."
                )

            # 2. Lakukan deteksi fake GPS jika data `position_data` diberikan
            if position_data:
                # Extract accuracy for early validation
                accuracy = position_data.get('coords', {}).get('accuracy')
                
                # Cek akurasi terlalu rendah (sinyal buruk atau indoor)
                # Ini adalah validasi terpisah dari deteksi fake GPS
                if accuracy is not None and accuracy > 50:
                    raise AppError(
                        400,
                        MESSAGE_CODE.BAD_REQUEST,
                        f"Akurasi GPS terlalu rendah ({accuracy:.2f}m). Harap tunggu hingga GPS mendapat sinyal yang lebih baik."
                    )
                
                if LocationService._detect_fake_gps(position_data):
                    raise AppError(
                        400,
                        MESSAGE_CODE.BAD_REQUEST,
                        "Terdeteksi penggunaan lokasi palsu. Harap gunakan lokasi asli untuk absensi."
                    )
            else:
                # Opsional: Jika position_data tidak ada, Anda bisa memilih untuk:
                # A. Mengizinkan (risiko lebih tinggi)
                # B. Melarang (lebih aman, tapi mungkin perlu penyesuaian di frontend)
                # Untuk keamanan, kita bisa anggap ini mencurigakan atau meminta data lengkap.
                # Atau tambahkan logging untuk memantau kasus ini.
                print("Warning: position_data not provided for location validation. Fake GPS detection skipped.")
                # raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Detail lokasi tidak lengkap untuk validasi keamanan.")


            # 3. Validasi jarak dari kantor (logika yang sudah ada)
            distance = LocationService.calculate_distance(
                OFFICE_LATITUDE,
                OFFICE_LONGITUDE,
                latitude,
                longitude
            )

            is_valid_distance = distance <= ALLOWED_RADIUS_KM

            if not is_valid_distance:
                raise AppError(
                    400, 
                    MESSAGE_CODE.BAD_REQUEST, 
                    f"Lokasi terlalu jauh dari kantor. Jarak: {distance:.2f}km (Maksimal: {ALLOWED_RADIUS_KM}km)"
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