
p_x = {
    1: 0.41,
    2: 0.25,
    3: 0.15,
    4: 0.10,
    5: 0.06,
    6: 0.03
}
p_y = {
    1: 0.12,
    2: 0.23,
    3: 0.31,
    4: 0.18,
    5: 0.12,
    6: 0.04,
    7: 0
}
def convolve(p_x, p_y):
    """Convolve the discrete probability densities https://www.youtube.com/watch?v=IaSGqQa5O-M&ab_channel=3Blue1Brown"""

    # Initialize the probability distribution dictionary.
    probability_distribution = {}

    # Iterate over the possible outcomes of the first probability distribution.
    for x, p_x_val in p_x.items():
        # Iterate over the possible outcomes of the second probability distribution.
        for y, p_y_val in p_y.items():
            s = x + y
            if s in probability_distribution:
                probability_distribution[s] += p_x_val * p_y_val
            else:
                probability_distribution[s] = p_x_val * p_y_val

    return probability_distribution


def main():
    print(convolve(p_x, p_y))

if __name__ == "__main__":
    main()