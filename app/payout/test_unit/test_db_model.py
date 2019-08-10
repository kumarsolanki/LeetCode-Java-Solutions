from typing import Type

import pytest

from app.commons.database.model import DBEntity, TableDefinition
from app.commons.test_unit.database.utils import validation_db_entity_and_table_schema
from app.payout.repository.maindb.model import PaymentAccountTable
from app.payout.repository.maindb.model.payment_account import (
    PaymentAccount,
    PaymentAccountUpdate,
    PaymentAccountCreate,
)
from app.payout.repository.maindb.model.stripe_managed_account import (
    StripeManagedAccount,
    StripeManagedAccountTable,
    StripeManagedAccountUpdate,
    StripeManagedAccountCreate,
)
from app.payout.repository.maindb.model.stripe_transfer import (
    StripeTransfer,
    StripeTransferTable,
    StripeTransferUpdate,
    StripeTransferCreate,
)
from app.payout.repository.maindb.model.transfer import (
    Transfer,
    TransferTable,
    TransferUpdate,
    TransferCreate,
)

test_db_entity_and_table_definition_data = [
    (PaymentAccount, PaymentAccountTable),
    (PaymentAccountCreate, PaymentAccountTable),
    (PaymentAccountUpdate, PaymentAccountTable),
    (StripeManagedAccount, StripeManagedAccountTable),
    (StripeManagedAccountCreate, StripeManagedAccountTable),
    (StripeManagedAccountUpdate, StripeManagedAccountTable),
    (Transfer, TransferTable),
    (TransferCreate, TransferTable),
    (TransferUpdate, TransferTable),
    (StripeTransfer, StripeTransferTable),
    (StripeTransferCreate, StripeTransferTable),
    (StripeTransferUpdate, StripeTransferTable),
]


@pytest.mark.parametrize(
    "db_entity_cls, table_definition_cls", test_db_entity_and_table_definition_data
)
def test_db_entity_and_table_definition(
    db_entity_cls: Type[DBEntity], table_definition_cls: Type[TableDefinition]
):
    validation_db_entity_and_table_schema(db_entity_cls, table_definition_cls)