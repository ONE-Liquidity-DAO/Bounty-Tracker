'''get result of campaign id'''
from tracker.bounty.bounty import get_bounty_info_from_campaign_id
from tracker.core.gsheet import GSheet
from tracker.core.logger import setup_logging
from tracker.account.account_validator import get_validated_account_infos
from tracker.connector.ccxt.get_config import CCXTConfig
from tracker.connector.ccxt.fetch_trades import TradeFetcher


class MockDataBase:
    '''mock database'''

    def commit_task_list_to_sql(self, tasks: list) -> None:
        '''commit list of tasks to database'''
        result = {}
        for sql_class in tasks:
            if sql_class.display_name not in result:
                result[sql_class.display_name] = 0
            if sql_class.takerOrMaker == 'maker':
                result[sql_class.display_name] += sql_class.amount
        print(result)


async def main():
    '''main script'''
    setup_logging()
    database = MockDataBase()
    gsheet = GSheet.create()
    account_infos = await get_validated_account_infos(gsheet)
    bounty_infos = [get_bounty_info_from_campaign_id(gsheet, 9)]
    print(bounty_infos)
    print(account_infos)
    config = CCXTConfig.create()
    fetcher = TradeFetcher(
        account_infos=account_infos,
        bounty_infos=bounty_infos,
        config=config,
        database=database,
    )
    await fetcher.start()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
