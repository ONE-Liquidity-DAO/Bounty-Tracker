'''gets and validate account info from google sheet'''
# pylint: disable=invalid-name
import asyncio
import logging
import gspread
from ccxt.base.errors import AuthenticationError
from tracker.core.gsheet import GSheet
from tracker.account.get_user_info import UserInfo
from tracker.account.create_account_infos import AccountInfo
logger = logging.getLogger(__name__)


async def validate_account_info(account_info: AccountInfo) -> None:
    '''loads the market and check if account can be validated'''
    try:
        await account_info.exchange.load_markets()
        await account_info.exchange.close()

    except AuthenticationError as error:
        account_info.user_info.valid = False
        account_info.user_info.reason = 'AuthenticationError'
        await account_info.exchange.close()
        logger.warning('%s: %s not able to be authenticated. skipping user',
                       account_info.user_info.display_name, error)
        return

    account_info.user_info.valid = True

def check_duplicated_api(account_infos: list[AccountInfo]) -> None:
    '''check for duplicated api key and disable them'''
    api_keys = []
    for account_info in account_infos:
        if account_info.user_info.api_key in api_keys:
            account_info.user_info.valid = False
            account_info.user_info.reason = 'DuplicatedError'
            logger.warning('duplicated api key: %s is duplicated, skipping user',
                           account_info.user_info.display_name)
        api_keys.append(account_info.user_info.api_key)

async def validate_account_infos(account_infos: list[AccountInfo]) -> None:
    '''run all validation account task asynchronously'''
    tasks = []
    check_duplicated_api(account_infos)
    for account_info in account_infos:
        tasks.append(validate_account_info(account_info))
    await asyncio.gather(*tasks)


def update_validity_in_sheet(user_infos: list[UserInfo], ws: gspread.Worksheet) -> None:
    '''
    update validity of user info back to google sheet
    This provides visual feedback to governor and user to check their api key
    '''

    valid_list = [user_info.valid for user_info in user_infos]
    reason_list = [user_info.reason for user_info in user_infos]
    cell_find = ws.find('valid', 1)
    valid_cells = ws.range(2, cell_find.col, len(valid_list)+1, cell_find.col)
    for i, cell in enumerate(valid_cells):
        cell.value = valid_list[i]
    ws.update_cells(valid_cells)
    cell_find = ws.find('reason', 1)
    reason_cells = ws.range(2, cell_find.col, len(valid_list)+1, cell_find.col)
    for i, cell in enumerate(reason_cells):
        cell.value = reason_list[i]
    ws.update_cells(reason_cells)


async def test() -> None:
    '''main function to run this module, mainly for testing purpose.'''
    sheet = GSheet.create()
    ws = sheet.user_info_ws

    user_infos = get_user_infos(sheet)
    account_infos = create_account_infos(user_infos)
    await validate_account_infos(account_infos)
    update_validity_in_sheet(user_infos, ws)

if __name__ == "__main__":
    import asyncio
    from tracker.account.get_user_info import get_user_infos
    from tracker.account.create_account_infos import create_account_infos
    from tracker.core.gsheet import GSheet
    asyncio.run(test())
