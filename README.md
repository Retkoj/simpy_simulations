# Simulations using simPy

## Setup

Created and tested using:
- Python 3.11
- Windows 11

Install the requirements:  
`python -m pip install requirements.txt`


## Run

### Movie theater simulation
Adapted from [this tutorial](https://realpython.com/simpy-simulating-with-python/)

Finds the best placing of employee resources to get moviegoers to their seats as fast as possible  
Assumes moviegoers arrive at an average of 12-second intervals (5 sec. std) and go through the following steps:  
- Buy a ticket from the cashier
- Get ticket checked by an usher
- Optionally (50-50) buy food from a server


To run (currently hardcoded for a maximum of 25 employees and 50 simulations per scenario):   
`python simulate_movie_theater.py`

Example output:  
```
The best average wait time is 3 minutes and 12 seconds, with 10 cashiers, 9 servers, 3 ushers
```