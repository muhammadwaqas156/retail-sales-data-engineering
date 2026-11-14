# Rule check results

## 1. Are all C rows Quantity < 0?
- C rows: 19,494 | with Quantity < 0: 19,493 | with Quantity >= 0: 1

## 2. Non-C rows with Quantity <= 0
- Count: 3,457
- Price == 0: 3,457
- Customer ID null: 3,457
- Description null: 2,689
- Top descriptions:

  - check: 123
  - damages: 84
  - ?: 83
  - damaged: 78
  - missing: 27
  - sold as set on dotcom: 20
  - Damaged: 17
  - smashed: 9
  - thrown away: 9
  - Unsaleable, destroyed.: 9

## 3. StockCodes not matching ^\d{5}[A-Za-z]*$
- Distinct codes: 63 | rows: 6,094
- Most common:

  - POST: 2,122
  - DOT: 1,446
  - M: 1,421
  - C2: 282
  - D: 177
  - S: 104
  - BANK CHARGES: 102
  - ADJUST: 67
  - AMAZONFEE: 43
  - DCGS0058: 31
  - gift_0001_20: 29
  - gift_0001_30: 29
  - DCGSSGIRL: 25
  - DCGSSBOY: 23
  - PADS: 19
  - gift_0001_10: 16
  - CRUK: 16
  - DCGS0076: 15
  - TEST001: 15
  - DCGS0003: 14
  - gift_0001_50: 8
  - gift_0001_40: 7
  - DCGS0069: 6
  - B: 6
  - DCGS0004: 5

## 4. Duplicates
- Duplicate rows (extra copies): 34,335 across 5,391 invoices
- Sample (first 10 rows):

|   Invoice |   StockCode | Description                     |   Quantity | InvoiceDate         |   Price |   Customer ID | Country        |
|----------:|------------:|:--------------------------------|-----------:|:--------------------|--------:|--------------:|:---------------|
|    489517 |       21491 | SET OF THREE VINTAGE GIFT WRAPS |          1 | 2009-12-01 11:34:00 |    1.95 |         16329 | United Kingdom |
|    489517 |       21491 | SET OF THREE VINTAGE GIFT WRAPS |          1 | 2009-12-01 11:34:00 |    1.95 |         16329 | United Kingdom |
|    489517 |       21821 | GLITTER STAR GARLAND WITH BELLS |          1 | 2009-12-01 11:34:00 |    3.75 |         16329 | United Kingdom |
|    489517 |       21821 | GLITTER STAR GARLAND WITH BELLS |          1 | 2009-12-01 11:34:00 |    3.75 |         16329 | United Kingdom |
|    489517 |       21912 | VINTAGE SNAKES & LADDERS        |          1 | 2009-12-01 11:34:00 |    3.75 |         16329 | United Kingdom |
|    489517 |       21912 | VINTAGE SNAKES & LADDERS        |          1 | 2009-12-01 11:34:00 |    3.75 |         16329 | United Kingdom |
|    489517 |       21912 | VINTAGE SNAKES & LADDERS        |          1 | 2009-12-01 11:34:00 |    3.75 |         16329 | United Kingdom |
|    489517 |       21913 | VINTAGE SEASIDE JIGSAW PUZZLES  |          1 | 2009-12-01 11:34:00 |    3.75 |         16329 | United Kingdom |
|    489517 |       21913 | VINTAGE SEASIDE JIGSAW PUZZLES  |          1 | 2009-12-01 11:34:00 |    3.75 |         16329 | United Kingdom |
|    489517 |       22130 | PARTY CONE CHRISTMAS DECORATION |          6 | 2009-12-01 11:34:00 |    0.85 |         16329 | United Kingdom |

## Extra: negative prices
- Rows: 5
Description
Adjust bad debt    5
