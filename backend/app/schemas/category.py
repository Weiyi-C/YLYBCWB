from pydantic import BaseModel, Field


class SubCategoryResponse(BaseModel):
    id: str
    name: str
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: str
    name: str
    type: str
    icon: str | None
    color: str
    sort_order: int
    is_system: bool
    is_active: bool
    sub_categories: list[SubCategoryResponse] = []

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    type: str = Field(pattern="^(expense|income)$")
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=7)
    sort_order: int | None = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=50)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=7)
    sort_order: int | None = None
    is_active: bool | None = None


class SubCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    sort_order: int | None = 0


class SubCategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=50)
    sort_order: int | None = None
    is_active: bool | None = None
