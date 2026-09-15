from pydantic import BaseModel,Field,field_validator,model_validator
from datetime import date
from typing import Optional


class UserCreate(BaseModel):
    full_name:str
    email:str
    phone:str
    dob:date
    password:str = Field(min_length=10)
    role:str
    subject:Optional[str]=None
    standard:Optional[str]=None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one alphabet")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")

        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain at least one special character")

        return value


    @model_validator(mode="after")
    def validate_role_fields(self):
        if self.role == "teacher":
            if not self.subject:
                raise ValueError("Subject is required for teachers")
            if self.standard:
                raise ValueError("Standard is not allowed for teachers")

        elif self.role == "student":
            if not self.standard:
                raise ValueError("Standard is required for students")
            if self.subject:
                raise ValueError("Subject is not allowed for students")

        elif self.role == "admin":
            if self.subject or self.standard:
                raise ValueError("Admin cannot have subject or standard")

        else:
            raise ValueError("Role must be admin, teacher, or student")

        return self


class ResendOTP(BaseModel):
    email:str

class OTPVerify(BaseModel):
    email:str
    otp:str



class UserLogin(BaseModel):
    email:str
    password:str




class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=10)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one alphabet")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")

        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain at least one special character")

        return value


class ForgotPasswordRequest(BaseModel):
    email: str



class ForgotPasswordVerifyOTP(BaseModel):
    email: str
    otp: str




class ResetPassword(BaseModel):
    new_password: str = Field(min_length=10)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one alphabet")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")

        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain at least one special character")

        return value



class AssignTeacher(BaseModel):
    teacher_id:int




class TeacherStudentResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    dob: date
    standard: str




class TeacherStudentUpdate(BaseModel):
    full_name: Optional[str]=None
    phone: Optional[str]=None
    dob: Optional[date]=None
    standard: Optional[str]=None




class StudentProfileResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    dob: date
    standard: str
    teacher: Optional[StudentTeacherResponse] = None




class StudentTeacherResponse(BaseModel):
    id: int
    full_name: str
    email: str
    subject: str




class AdminStudentResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    dob: date
    standard: str
    teacher_id: Optional[int] = None



class AdminTeacherResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    dob: date
    subject: str



class AdminUserCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    dob: date
    role: str

    subject: Optional[str] = None
    standard: Optional[str] = None

    @model_validator(mode="after")
    def validate_role_fields(self):
        if self.role == "teacher":
            if not self.subject:
                raise ValueError("Subject is required for teachers")

            if self.standard:
                raise ValueError("Standard is not allowed for teachers")

        elif self.role == "student":
            if not self.standard:
                raise ValueError("Standard is required for students")

            if self.subject:
                raise ValueError("Subject is not allowed for students")

        else:
            raise ValueError("Admin can only create teachers or students")

        return self



class FirstLoginOTPVerify(BaseModel):
    user_id: int
    otp: str





class FirstLoginPasswordChange(BaseModel):
    new_password: str = Field(min_length=10)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")

        if not any(char in "!@#$%^&*" for char in value):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value



class AdminStudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    standard: Optional[str] = None
    teacher_id: Optional[int] = None



class AdminTeacherUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    subject: Optional[str] = None





class AdminRoleUpdate(BaseModel):
    role: str
    subject: Optional[str] = None
    standard: Optional[str] = None

    @model_validator(mode="after")
    def validate_role_fields(self):
        if self.role == "teacher":
            if not self.subject:
                raise ValueError("Subject is required for teachers")

            if self.standard:
                raise ValueError("Standard is not allowed for teachers")

        elif self.role == "student":
            if not self.standard:
                raise ValueError("Standard is required for students")

            if self.subject:
                raise ValueError("Subject is not allowed for students")

        else:
            raise ValueError(
                "Admin can only assign teacher or student role"
            )

        return self