## Public Ledger Market Experiment? 

This project implements a multi-stage market experiment using the oTree platform. The game simulates a market environment where six players interact in a structured trading process. Players assume the roles of one producer, two sellers, and three buyers, each with specific decision-making responsibilities. The game unfolds in multiple rounds: first, sellers bid for production bases from the producer, and the producer decides whether to accept or reject these offers. Once sellers acquire a base, they can produce 2 products with one base and can set a price for their products. Before buyers can purchase, they participate in a guessing game, where they estimate a randomly generated number between 1 and 100. The buyers are then ranked based on the accuracy of their guesses, determining their purchasing order. Buyers take turns purchasing products from sellers, ensuring a first-come, first-served market mechanism where stock availability dynamically updates after each transaction. During all rounds, and decision process, a public ledger records all transactions and displayed to everyone, ensuring transparency for all participants. The project emphasizes strategic decision-making, dynamic stock updates, and fair buyer ranking under public ledger structure, making it a robust simulation for understanding market behaviors and competitive pricing strategies.

This experiment is to understand the market behaviour of product makers, sellers, and customers under public ledger. The structure is solely designed by the owner of this account, and does not reflect any instiutitional ideas. 

## Initial stage of tokens, products, and bases.

- Producer: 2 bases, 0 products, 0 token.
- Seller: 0 bases, 0 products, 3 tokens.
- Buyer: 0 bases, 0 products, 5 tokens. 

At the end of the game rewards are allocated based on the following structure:

- Producer: Base = 1.5 Points; Tokens = 1 Point. 
- Seller: Product = 0 Points; Tokens = 2 Points. 
- Buyer: Product = 3 Points; Tokens = 0.5 Points. 

- Points = 2$ (Given in the end of the experiment.)

Numbers are choosen loosely, they are open to adjustment. 

To access to project, please download the [zip file](https://github.com/FurkanDanisman/PublicLedgerExperiment-Otree/blob/main/market_experience.otreezip). 

To access to the [python code](https://github.com/FurkanDanisman/PublicLedgerExperiment-Otree/tree/main/ledger_demo/__init__.py) and html codes please access to [ledger_demo](https://github.com/FurkanDanisman/PublicLedgerExperiment-Otree/tree/main/ledger_demo). 
