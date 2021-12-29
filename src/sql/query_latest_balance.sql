SELECT *
FROM Balances
where account_name || timestamp in 
    -- get max timestamp for each account name and concat them from balance
(
    SELECT account_name || MAX(timestamp) as id
    FROM Balances
    -- only get account with recent updates in the past 1 week
    WHERE timestamp > strftime('%s', 'now') * 1000 - 7*24*60*60*1000
    GROUP BY account_name
);