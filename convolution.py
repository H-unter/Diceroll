import numpy as np
from scipy.signal import fftconvolve

def convolve(p_x, p_y):
    """Convolve the discrete probability densities https://www.youtube.com/watch?v=IaSGqQa5O-M&ab_channel=3Blue1Brown"""
    outcome_to_probability = {}
    for x, p_x_val in p_x.items():# Iterate over the possible outcomes of the first probability distribution.
        for y, p_y_val in p_y.items():# Iterate over the possible outcomes of the second probability distribution.
            s = x + y
            if s in outcome_to_probability:
                outcome_to_probability[s] += p_x_val * p_y_val
            else:
                outcome_to_probability[s] = p_x_val * p_y_val
    return outcome_to_probability


def numpy_convolve(p_x, p_y):
    """Convolve the discrete probability densities using numpy"""
    x = np.array(list(p_x.keys()))
    y = np.array(list(p_y.keys()))
    p_x = np.array(list(p_x.values()))
    p_y = np.array(list(p_y.values()))
    convolved = np.convolve(p_x, p_y).astype(float)
    
    # Create the outcome to probability dictionary
    outcome_to_probability = {i + j: convolved[i + j] for i in range(len(x)) for j in range(len(y))}
    return outcome_to_probability

def fft_convolve(p_x, p_y):
    """Convolve the discrete probability densities using scipy's fftconvolve"""
    
    x = np.array(list(p_x.keys()))
    y = np.array(list(p_y.keys()))
    p_x = np.array(list(p_x.values()))
    p_y = np.array(list(p_y.values()))
    convolved = fftconvolve(p_x, p_y, mode='full')
    
    # Create the outcome to probability dictionary
    outcome_to_probability = {i + j: convolved[i + j] for i in range(len(x)) for j in range(len(y))}
    return outcome_to_probability


def benchmark_convolution_implementations():
    """Benchmark various convolution implementations and plot the output"""

    import timeit
    import matplotlib.pyplot as plt

    my_input_length_to_compute_time = {}
    numpy_input_length_to_compute_time = {}
    fft_input_length_to_compute_time = {}
    input_lengths = range(10, 200, 20)  # Adjust the step size for faster computation

    for input_length in input_lengths:
        np.random.seed(0)  # Set seed for reproducibility
        p_x = {i: np.random.random() for i in range(input_length)}
        np.random.seed(1)  # Set seed for reproducibility
        p_y = {i: np.random.random() for i in range(input_length)}

        my_time = timeit.timeit(lambda: convolve(p_x, p_y), number=500)
        numpy_time = timeit.timeit(lambda: numpy_convolve(p_x, p_y), number=500)
        fft_time = timeit.timeit(lambda: fft_convolve(p_x, p_y), number=500)

        my_input_length_to_compute_time[input_length] = my_time
        numpy_input_length_to_compute_time[input_length] = numpy_time
        fft_input_length_to_compute_time[input_length] = fft_time


    plt.plot(list(my_input_length_to_compute_time.keys()), list(my_input_length_to_compute_time.values()), label="My implementation")
    plt.plot(list(numpy_input_length_to_compute_time.keys()), list(numpy_input_length_to_compute_time.values()), label="Numpy implementation")
    plt.plot(list(fft_input_length_to_compute_time.keys()), list(fft_input_length_to_compute_time.values()), label="Scipy FFT implementation")
    plt.xlabel("Input length")
    plt.ylabel("Time (s)")
    # plt.yscale('log')
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    benchmark_convolution_implementations()