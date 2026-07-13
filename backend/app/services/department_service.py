from uuid import UUID
from app.core.exceptions import ValidationException, ResourceNotFoundException, ResourceConflictException
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate

class DepartmentService:
    def __init__(self, department_repo: DepartmentRepository):
        self.department_repo = department_repo
        
    async def create_department(self, payload: DepartmentCreate):
        if await self.department_repo.get_by_code(payload.code):
            raise ValidationException("Department code already exists")
        if await self.department_repo.get_by_name(payload.name):
            raise ValidationException("Department name already exists")
            
        return await self.department_repo.create(payload)
        
    async def get_department(self, dept_id: UUID):
        dept = await self.department_repo.get_by_id(dept_id)
        if not dept:
            raise ResourceNotFoundException("Department")
        return dept
        
    async def list_departments(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ):
        return await self.department_repo.list(
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
    async def update_department(self, dept_id: UUID, payload: DepartmentUpdate):
        dept = await self.get_department(dept_id)
        
        if payload.code and payload.code != dept.code:
            if await self.department_repo.get_by_code(payload.code):
                raise ValidationException("Department code already exists")
                
        if payload.name and payload.name != dept.name:
            if await self.department_repo.get_by_name(payload.name):
                raise ValidationException("Department name already exists")
                
        update_data = payload.model_dump(exclude_unset=True)
        return await self.department_repo.update(dept, **update_data)
        
    async def delete_department(self, dept_id: UUID):
        dept = await self.get_department(dept_id)
        try:
            await self.department_repo.delete(dept)
        except Exception as e:
             raise ResourceConflictException("Cannot delete department because users are assigned to it")
