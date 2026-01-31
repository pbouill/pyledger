from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from canon.enums.account import AccountType
from canon.models import Base
from canon.models.account import Account


async def test_account_model_smoke() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    conn = await engine.connect()
    try:
        await conn.run_sync(Base.metadata.create_all)
        session_maker = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with session_maker() as s:
            a = Account(
                name="Primary Checking",
                institution="Bank X",
                currency_code="USD",
                account_type=AccountType.CHEQUING,
            )
            s.add(a)
            await s.commit()
            await s.refresh(a)
            assert a.id is not None
            res = await s.execute(select(Account).where(Account.id == a.id))
            assert res.scalar_one_or_none() is not None
    finally:
        await conn.close()
