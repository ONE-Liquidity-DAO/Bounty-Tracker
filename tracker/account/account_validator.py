'''
main function for account
'''
import asyncio

from tracker.account.create_account_infos import AccountInfo, create_account_infos
from tracker.account.get_user_info import get_user_infos
from tracker.account.validation import (update_validity_in_sheet,
                                    validate_account_infos)
from tracker.core.gsheet import GSheet


async def get_validated_account_infos(g_sheet: GSheet) -> list[AccountInfo]:
    '''get only valid account info'''
    worksheet = g_sheet.user_info_ws
    user_infos = get_user_infos(g_sheet)
    account_infos = create_account_infos(user_infos)
    await validate_account_infos(account_infos)
    update_validity_in_sheet(user_infos, worksheet)
    return [account_info for account_info in account_infos if account_info.user_info.valid]


class AccountValidator:
    '''a class to update account infos at specified interval from google sheet'''

    def __init__(self,
                 g_sheet: GSheet,
                 account_infos: list[AccountInfo] = None,
                 update_interval: int = 3600) -> None:
        self.g_sheet = g_sheet
        self.account_infos = account_infos
        self.update_interval = update_interval

    @classmethod
    async def create(cls, g_sheet: GSheet, update_interval: float = 3600) -> 'AccountValidator':
        '''a default method of starting account validator'''
        account_infos = await get_validated_account_infos(g_sheet)
        return cls(g_sheet=g_sheet, account_infos=account_infos, update_interval=update_interval)

    async def start(self) -> None:
        '''starts a async loop to periodically validated account info'''
        while True:
            try:
                self.account_infos = await get_validated_account_infos(self.g_sheet)
                await asyncio.sleep(self.update_interval)
            except KeyboardInterrupt:
                break


async def test():
    '''test for this module.'''
    sheet = GSheet.create()
    account_validator = await AccountValidator.create(sheet)
    await account_validator.start()

if __name__ == '__main__':
    import asyncio
    asyncio.run(test())
