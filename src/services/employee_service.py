from io import BytesIO
import os
import dlib
import numpy as np
from PIL import Image
from sqlalchemy.orm import Session
from src.repositories.employee_repository import EmployeeRepository
from src.libs.supabase import upload_image_to_supabase
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE
from typing import Optional, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models-face")

SP_MODEL_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")
FACE_REC_MODEL_PATH = os.path.join(MODEL_DIR, "dlib_face_recognition_resnet_model_v1.dat")

# Initialize face recognition models
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(SP_MODEL_PATH)
face_rec_model = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)

class EmployeeService:
    # @staticmethod
    # def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List:
    #     return EmployeeRepository.get_all(db, skip, limit)
    
    @staticmethod
    def get_all_employees(db: Session, page: int = 1, per_page: int = 10, search: str = None):
        return EmployeeRepository.get_all(db, page, per_page, search)

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int):
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Employee not found")
        return employee

    @staticmethod
    async def create_employee(db: Session, name: str, email: str, date_of_birth, divisi: str, address: str, image_data: bytes = None):
        # Check if email already exists
        if EmployeeRepository.get_by_email(db, email):
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email already exists")

        face_encoding = EmployeeService.extract_face_encoding(image_data)
        if isinstance(face_encoding, AppError):
            raise face_encoding
        image_url = await upload_image_to_supabase(image_data)
        if isinstance(image_url, AppError):
            raise image_url
        

        employee = EmployeeRepository.create(db, name, email, date_of_birth, divisi, address, image_url, face_encoding)
        return employee

    @staticmethod
    async def update_employee(db: Session, employee_id: int, name: str = None, email: str = None, 
                            date_of_birth=None, divisi: str = None, address: str = None, image_data: bytes = None):
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Employee not found")

        # Check if email already exists (but not for current employee)
        if email and email != employee.email:
            existing_employee = EmployeeRepository.get_by_email(db, email)
            if existing_employee:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email already exists")

        image_url = employee.image_url
        face_encoding = employee.face_encoding
        if image_data:
            face_encoding = await EmployeeService.extract_face_encoding(image_data)
            if isinstance(face_encoding, AppError):
                raise face_encoding
            image_url = await upload_image_to_supabase(image_data)
            if isinstance(image_url, AppError):
                raise image_url

        updated_employee = EmployeeRepository.update(
            db, employee_id,
            name=name, email=email, date_of_birth=date_of_birth,
            divisi=divisi, address=address, image_url=image_url, face_encoding=face_encoding
        )
        return updated_employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int):
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Employee not found")

        # Check if employee has associated user
        if hasattr(employee, 'user') and employee.user:
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Cannot delete employee with associated user account")

        success = EmployeeRepository.delete(db, employee_id)
        if not success:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, "Failed to delete employee")
        return {"message": "Employee deleted successfully"}
    
    @staticmethod
    def verify_face(db: Session, image_data: bytes):
        """
        Verify face and return employee data if match found
        """
        try:
            # Convert image data to numpy array
            image = Image.open(BytesIO(image_data)).convert("RGB")
            img = np.array(image)

            # Detect faces
            faces = detector(img)
            if len(faces) == 0:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "No face detected in the image")

            # Get face encoding
            shape = sp(img, faces[0])
            face_encoding = np.array(face_rec_model.compute_face_descriptor(img, shape))

            # Get all employees with face data
            employees = EmployeeRepository.get_all_with_face_data(db)
            
            if not employees:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "No registered faces found")

            # Compare with stored face encodings
            best_match = None
            best_distance = float('inf')
            
            for employee in employees:
                if employee.face_encoding:
                    try:
                        # Parse stored face encoding
                        stored_encoding = np.array(list(map(float, employee.face_encoding.split(','))))
                        
                        # Calculate distance
                        distance = np.linalg.norm(face_encoding - stored_encoding)
                        
                        # Check if this is the best match so far
                        if distance < best_distance:
                            best_distance = distance
                            best_match = employee
                    except (ValueError, AttributeError):
                        # Skip if face encoding is malformed
                        continue

            # Check if best match is within threshold
            if best_match and best_distance < 0.6:
                return {
                    "id": best_match.id,
                    "name": best_match.name,
                    "email": best_match.email,
                    "divisi": best_match.divisi,
                    "image_url": best_match.image_url,
                    "confidence": 1 - (best_distance / 1.0)  # Convert distance to confidence score
                }
            else:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Face not recognized")

        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Face verification failed: {str(e)}")

    @staticmethod
    def extract_face_encoding(image_data: bytes):
        """
        Extract face encoding from image data for storage
        """
        try:
            image = Image.open(BytesIO(image_data)).convert("RGB")
            img = np.array(image)

            faces = detector(img)
            if len(faces) == 0:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "No face detected in the image")

            shape = sp(img, faces[0])
            face_encoding = np.array(face_rec_model.compute_face_descriptor(img, shape))
            
            # Convert to comma-separated string for storage
            return ','.join(map(str, face_encoding))

        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Face encoding extraction failed: {str(e)}")