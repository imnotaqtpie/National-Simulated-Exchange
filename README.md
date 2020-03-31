# README #

Code for a simulated exchange

### What is this repository for? ###

This repo contains the code for a model stock exchange built in python. It currently supports limit orders where a player can place new orders, modify them or delete them.

All players start out with 10000 credit point which they can use to trade. The market movements are decided by the players movements with the last traded price used to determine price movements. Players can place new orders, modify them or delete them as they wish. We also broadcast every single update (known as a tick) to all players connected to the exchange. 
This book data can be used to players to run trading algorithms since all major inferences can be drawn by looking at the order book data. This data can also be used to understand the market dynamics of a limit order book in a model environment. 

version 0.0

### How do I get set up? ###

* To start, players need to setup a postgresql server. The login credentials need to be provided in exchange_server_manager.py file

### Who do I talk to? ###

Creators of this page are : 
* Anuroop Behera (@imnotaqtpie)
* RSB Balaji (@RSB-Balaji)
