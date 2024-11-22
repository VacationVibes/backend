from fastapi import HTTPException


class InvalidPlaceException(HTTPException):
    def __init__(self, detail: str = "This place does not exist", status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)
