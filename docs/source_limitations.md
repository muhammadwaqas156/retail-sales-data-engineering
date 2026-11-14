# Source limitations
- UCI Online Retail II is historical (1 Dec 2009 to 9 Dec 2011) from one UK-based online giftware retailer. Not current, not Tesco.
- 22.77% of lines have no Customer ID, so customer analysis covers known customers only.
- DummyJSON is synthetic. IDs do not join to UCI data. Never present it as real sales.
- DummyJSON users include fake sensitive-looking fields (password, ssn, bank, crypto, ein, macAddress, ip). Drop these at ingestion or staging, never show them in screenshots or posts, and keep raw files out of Git (already gitignored).
