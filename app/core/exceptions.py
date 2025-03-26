from fastapi import HTTPException

class MetalabsAPIError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class AuthenticationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Неверные учетные данные") 