
from decimal import Decimal

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

    async def find_limited_by_category(
        self,
        category: str,
        premium_min: Decimal | None,
        limit: int,
    ) -> list[Product]:
        conditions = [
            Product.status == "active",
            Product.category == category,
        ]
        if premium_min is not None:
            conditions.append(Product.min_premium < premium_min)

        products = await self.session.scalars(
            select(Product)
            .where(*conditions)
            .order_by(
                Product.min_premium.asc().nullslast(),
                Product.id.asc(),
            )
            .limit(limit)
        )
        return list(products.all())

    async def find_candidates(
        self,
        categories: list[str],
        premium_min: Decimal | None,
        limit_per_category: int,
    ) -> list[Product]:
        # 每个险种查limit_per_category条，所以先定义list，收集结果
        candidate_products: list[Product] = []

        # 利用dict去重，并保留调用方传入的险种顺序，然后遍历逐个查询
        for category in dict.fromkeys(categories):
            conditions = [
                Product.status == "active",
                Product.category == category,
            ]
            if premium_min is not None:
                conditions.append(Product.min_premium < premium_min)

            products = await self.session.scalars(
                select(Product)
                .where(*conditions)
                .order_by(
                    Product.min_premium.asc().nullslast(),
                    Product.id.asc(),
                )
                .limit(limit_per_category)
            )
            candidate_products.extend(products.all())

        return candidate_products