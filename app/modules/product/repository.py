
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_by_category(self, category: str | None = None) -> list[Product]:
        # 动态条件
        conditions = [Product.status == 'active']
        if category:
            conditions.append(Product.category == category)

        result = await self.session.execute(
            select(Product)
            .where(*conditions)
            .order_by(Product.id.asc())
        )

        return list(result.scalars().all())
