-- SQLite
SELECT account_name, symbol, MAX("order")
FROM Trades
GROUP BY account_name, symbol