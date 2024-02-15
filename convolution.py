
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

    # define the outcomes for each die
    die_1_outcomes = list(p_x.keys())
    die_2_outcomes = list(p_y.keys())
    #iterate over values of s
    s_min = die_1_outcomes[0]+die_2_outcomes[0]
    s_max = die_1_outcomes[-1]+die_2_outcomes[-1]
    probability_distribution = {outcome: 0 for outcome in range(s_min, s_max + 1)}
    for s in range(s_min, s_max + 1):
        for x in p_x.keys():
            try:
                probability_distribution[s] += p_x[x]*p_y[s-x]
            except KeyError:
                pass # out of range key means a probability of 0
        #print(f"p_x({x}) * p_y({y}) + \n")
    print(probability_distribution)
    return probability_distribution


def main():
    print(convolve(p_x, p_y))

if __name__ == "__main__":
    main()