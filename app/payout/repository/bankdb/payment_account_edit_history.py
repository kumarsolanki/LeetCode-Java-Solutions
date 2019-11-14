from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import and_, desc
from typing_extensions import final

from app.commons import tracing
from app.commons.database.infra import DB
from app.payout.models import BankUpdateHistoryOwnerType
from app.payout.repository.bankdb.base import PayoutBankDBRepository
from app.payout.repository.bankdb.model import payment_account_edit_history
from app.payout.repository.bankdb.model.payment_account_edit_history import (
    PaymentAccountEditHistory,
    PaymentAccountEditHistoryCreate,
)


class PaymentAccountEditHistoryRepositoryInterface(ABC):
    @abstractmethod
    async def get_most_recent_bank_update(
        self, payment_account_id: int, within_last_timedelta: Optional[timedelta] = None
    ) -> Optional[PaymentAccountEditHistory]:
        pass

    @abstractmethod
    async def get_bank_updates_for_store_with_payment_account_and_time_range(
        self, payment_account_id: int, start_time: datetime, end_time: datetime
    ) -> List[PaymentAccountEditHistory]:
        pass

    @abstractmethod
    async def get_recent_bank_update_payment_account_ids(
        self, last_bank_account_update_allowed_at: datetime
    ) -> List[int]:
        pass

    @abstractmethod
    async def record_bank_update(
        self, data: PaymentAccountEditHistoryCreate
    ) -> PaymentAccountEditHistory:
        pass


@final
@tracing.track_breadcrumb(repository_name="payment_account_edit_history")
class PaymentAccountEditHistoryRepository(
    PayoutBankDBRepository, PaymentAccountEditHistoryRepositoryInterface
):
    def __init__(self, database: DB):
        super().__init__(_database=database)

    async def get_most_recent_bank_update(
        self, payment_account_id: int, within_last_timedelta: Optional[timedelta] = None
    ) -> Optional[PaymentAccountEditHistory]:
        query = and_(
            payment_account_edit_history.payment_account_id.isnot(None),
            payment_account_edit_history.payment_account_id == payment_account_id,
        )
        if within_last_timedelta:
            since_date = datetime.utcnow() - within_last_timedelta
            query.clauses.append(
                payment_account_edit_history.timestamp.__gt__(since_date)
            )
        stmt = (
            payment_account_edit_history.table.select()
            .where(query)
            .order_by(desc(payment_account_edit_history.timestamp))
        )
        row = await self._database.replica().fetch_one(stmt)
        return PaymentAccountEditHistory.from_row(row) if row else None

    async def get_recent_bank_update_payment_account_ids(
        self, last_bank_account_update_allowed_at: datetime
    ) -> List[int]:
        stmt = (
            payment_account_edit_history.table.select()
            .distinct(payment_account_edit_history.payment_account_id)
            .where(
                payment_account_edit_history.timestamp.__ge__(
                    last_bank_account_update_allowed_at
                )
            )
        )
        rows = await self._database.replica().execute(stmt)
        result: List[int] = []
        for row in rows:
            result.append(row.get("payment_account_id"))
        return result

    async def get_bank_updates_for_store_with_payment_account_and_time_range(
        self, payment_account_id: int, start_time: datetime, end_time: datetime
    ) -> List[PaymentAccountEditHistory]:
        query = and_(
            payment_account_edit_history.payment_account_id == payment_account_id,
            payment_account_edit_history.owner_type == BankUpdateHistoryOwnerType.STORE,
            payment_account_edit_history.timestamp.__ge__(start_time),
            payment_account_edit_history.timestamp.__le__(end_time),
        )
        stmt = payment_account_edit_history.table.select().where(query)
        rows = await self._database.replica().fetch_all(stmt)
        if rows:
            return [PaymentAccountEditHistory.from_row(row) for row in rows]
        else:
            return []

    async def record_bank_update(
        self, data: PaymentAccountEditHistoryCreate
    ) -> PaymentAccountEditHistory:
        ts_now = datetime.utcnow()
        stmt = (
            payment_account_edit_history.table.insert()
            .values(data.dict(skip_defaults=True), timestamp=ts_now)
            .returning(*payment_account_edit_history.table.columns.values())
        )
        row = await self._database.master().fetch_one(stmt)
        assert row is not None
        return PaymentAccountEditHistory.from_row(row)
