'''
main interface to update the account info
'''
from src.account.create_account_infos import AccountInfo, create_account_infos
from src.account.get_user_info import get_user_infos
from src.account.validate_account_infos import update_validity_in_sheet, validate_account_infos
from src.core.gsheet import GSheet

async def get_validated_account_infos(g_sheet: GSheet) -> list[AccountInfo]:
    '''get only valid account info'''
    worksheet = g_sheet.user_info_ws
    user_infos = get_user_infos(g_sheet)
    account_infos = create_account_infos(user_infos)
    await validate_account_infos(account_infos)
    update_validity_in_sheet(user_infos, worksheet)
    return [account_info for account_info in account_infos if account_info.user_info.valid]

if __name__ == '__main__':
    import asyncio
    sheet = GSheet.create()
    print(asyncio.run(get_validated_account_infos(sheet)))