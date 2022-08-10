from math import sqrt
from scipy.stats import norm
from pandas import DataFrame
from numpy import asarray, empty, expand_dims
from numpy.core.fromnumeric import cumsum

from pprint import pprint


class BrownianMotion:
    @staticmethod
    def brownian(
        time_step, delta, initial_value=100, steps=1, total_lines=1, length_of_candle=10
    ):
        # Create an empty array to store the realizations.
        x = empty((total_lines, steps + 1))
        initial_values = x[:, 0] = initial_value
        initial_values = asarray(initial_values)

        # For each element of initial_values, generate a sample of n numbers from a
        # normal distribution.
        r = norm.rvs(
            size=initial_values.shape + (steps,), scale=delta * sqrt(time_step)
        )

        # create an output array.
        output = empty(r.shape)

        # This computes the Brownian motion by forming the cumulative sum of
        # the random samples.
        cumsum(r, axis=-1, out=output)

        # Add the initial condition.
        output += expand_dims(initial_values, axis=-1)

        open = []
        high = []
        low = []
        close = []

        start = 0
        end = len(output) - 1
        while start < end:
            candle = output[start : min(end, (length_of_candle + start))]

            open.append(candle[0])
            high.append(max(candle))
            low.append(min(candle))
            close.append(candle[-1])

            start += length_of_candle

        data = {"open": open, "high": high, "low": low, "close": close}

        return DataFrame(data=data)


#
# import numpy
# from pylab import plot, show, grid, xlabel, ylabel
#
# # The Wiener process parameter.
# delta = 2
# # Total time.
# T = 10.0
# # Number of steps.
# N = 500
# # Time step size
# dt = T/N
# # Number of realizations to generate.
# m = 20
# # Create an empty array to store the realizations.
# x = numpy.empty((m,N+1))
# # Initial values of x.
# x[:, 0] = 50
#
# brownian(x[:,0], N, dt, delta, out=x[:,1:])
#
# t = numpy.linspace(0.0, N*dt, N+1)
# for k in range(m):
#     plot(t, x[k])
# xlabel('t', fontsize=16)
# ylabel('x', fontsize=16)
# grid(True)
# show()
