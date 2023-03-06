import random
import statistics
from typing import Generator

from simpy import Environment, Resource

wait_times = []


class MovieTheater:
    def __init__(self, env: Environment, n_cashiers: int, n_ushers: int, n_servers: int):
        self.env = env
        self.cashier = Resource(self.env, n_cashiers)
        self.usher = Resource(self.env, n_ushers)
        self.server = Resource(self.env, n_servers)

    def sell_ticket(self, moviegoer):
        """takes 1 - 3 minutes"""
        yield self.env.timeout(random.randint(1, 3))

    def check_ticket(self, moviegoer):
        """takes avg. 3 seconds"""
        n_seconds = random.normalvariate(3 / 60, 1 / 60)
        while n_seconds < 0:
            n_seconds = random.normalvariate(3 / 60, 1 / 60)
        yield self.env.timeout(n_seconds)

    def sell_food(self, moviegoer):
        """takes 1 - 5 minutes"""
        yield self.env.timeout(random.randint(1, 5))


def go_to_movies(env: Environment, moviegoer: int, movie_theater: MovieTheater) -> Generator:
    """
    Simulate a single moviegoer's path from arriving at the movie theater until being seated, in terms of
    services provided by the theater.
    - Buying a ticket
    - Having the ticket checked
    - Optionally, buying food (50% chance)

    The time spend is then added to the global variable wait_times

    :param env: Environment, the simpy environment
    :param moviegoer: int, id of the current moviegoer
    :param movie_theater: MovieTheater, the theater
    """
    arrival_time = env.now

    with movie_theater.cashier.request() as request:
        yield request
        yield env.process(movie_theater.sell_ticket(moviegoer))

    with movie_theater.usher.request() as request:
        yield request
        yield env.process(movie_theater.check_ticket(moviegoer))

    if random.choice([True, False]):
        with movie_theater.server.request() as request:
            yield request
            yield env.process(movie_theater.sell_food(moviegoer))

    wait_times.append(env.now - arrival_time)


def get_moviegoer():
    """Generator for moviegoer ID's"""
    n = 0
    while True:
        yield n
        n += 1


def run_movie_theater(env: Environment, n_cashiers: int, n_servers: int, n_ushers: int) -> Generator:
    """
    Creates a movie theater,
    assumes moviegoers arrive at an average of 12-second intervals, with a 5-second standard deviation,
    processes moviegoers infinitely
    """
    movie_theater = MovieTheater(env, n_cashiers, n_ushers, n_servers)

    moviegoer = get_moviegoer()

    arrival_interval = random.normalvariate(12/60, 5/60)
    while arrival_interval < 0:
        arrival_interval = random.normalvariate(12 / 60, 5 / 60)
    while True:
        yield env.timeout(arrival_interval)
        env.process(go_to_movies(env, next(moviegoer), movie_theater))


def get_average_wait_time(times: list) -> tuple[int, int]:
    """Returns the average number of minutes and seconds of times """
    average_wait = statistics.mean(times)
    # Pretty print the results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)


def get_user_input() -> tuple[int, int, int]:
    """
    Optional function, to get parameters from user instead of permutation function
    :return: tuple, num_cashiers, num_servers, num_ushers
    """
    num_cashiers = input("Input # of cashiers working: ")
    num_servers = input("Input # of servers working: ")
    num_ushers = input("Input # of ushers working: ")
    params = num_cashiers, num_servers, num_ushers
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. The simulation will use default values:",
            "\n1 cashier, 1 server, 1 usher.",
        )
        params = 1, 1, 1
    return params


def get_parameter_permutation(total_employees: int) -> tuple[int, int, int]:
    """
    Generator function to get the number of cashiers, servers and ushers.
    Makes permutations up to a total number of employees (total_employees)

    :param total_employees: int, the number of cashiers, servers and ushers
    :yield: tuple, num_cashiers, num_servers, num_ushers
    """
    for num_cashiers in range(1, total_employees - 1):
        servers_and_ushers = total_employees - num_cashiers
        for num_servers in range(1, servers_and_ushers):
            possible_ushers = servers_and_ushers - num_servers
            for num_ushers in range(1, possible_ushers):
                yield num_cashiers, num_servers, num_ushers


def main(random_seed: int = 42, total_employees: int = 25, simulation_runs: int = 50):
    """
    Runs the entire simulation. If a simulation is better than the best_setup, replaces best_setup.
    Prints best results to command line when finished.

    :param random_seed: int, ensure repeatable results
    :param total_employees: int, total number of employees at movie theater, used in parameter permutation setup
    :param simulation_runs: int, number of simulations to run per permutation
    :return:
    """
    random.seed(random_seed)
    best_setup = {"avg_wait_time": float('inf'),
                  "wait_times": [],
                  "n_cashiers": 0,
                  "n_servers": 0,
                  "n_ushers": 0}

    # Run simulations
    for num_cashiers, num_servers, num_ushers in get_parameter_permutation(total_employees=total_employees):
        global wait_times
        wait_times = []

        env = Environment()
        env.process(run_movie_theater(env, num_cashiers, num_servers, num_ushers))
        env.run(until=simulation_runs)

        # View the results
        avg_wait_time = statistics.mean(wait_times)
        if avg_wait_time < best_setup["avg_wait_time"]:
            best_setup["avg_wait_time"] = avg_wait_time
            best_setup["wait_times"] = wait_times
            best_setup["n_cashiers"] = num_cashiers
            best_setup["n_servers"] = num_servers
            best_setup["n_ushers"] = num_ushers

    mins, secs = get_average_wait_time(best_setup["wait_times"])
    print(
        f"\nThe best average wait time is {mins} minutes and {secs} seconds, "
        f"with {best_setup['n_cashiers']} cashiers, {best_setup['n_servers']} servers, "
        f"{best_setup['n_ushers']} ushers"
    )


if __name__ == '__main__':
    main()
