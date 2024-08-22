"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import matplotlib.pyplot
import math
import convolution # custom module for convolution of probability distributions

is_results_displayed = True

def main():
    """Calculate the probability distribution of a die roll prompt"""
    # prompt = input("Enter Dice: ")  # 2d6+1
    dice_prompt = "10d10+3"
    number_of_dice, number_of_faces, modifier = parse_dice_prompt(dice_prompt)
    outcome_to_probability = calculate_pdf(number_of_faces, number_of_dice, modifier)
    outcome_to_cumulative_probability = calculate_cdf(outcome_to_probability)
    mean_value = calculate_mean(outcome_to_probability)  # change to "expected_outcome"?
    if is_results_displayed:
        display_numerical_results(dice_prompt, outcome_to_cumulative_probability)
    plot_values(dice_prompt, outcome_to_probability, mean_value)


def parse_dice_prompt(dice_prompt):
    """Parse dice prompt and return the 3 characteristic parameters XdY+Z"""
    number_of_dice, remainder = dice_prompt.split('d')
    number_of_faces, modifier = remainder.split('+')
    return int(number_of_dice), int(number_of_faces), int(modifier)


def calculate_pdf(number_of_faces, number_of_dice, modifier):
    """Convolve the discrete probability densities https://www.youtube.com/watch?v=IaSGqQa5O-M&ab_channel=3Blue1Brown"""
    die_face_probability = 1 / number_of_faces
    single_die_range = range(1 + modifier, number_of_faces + modifier + 1)
    die_probability_distribution = {outcome: die_face_probability for outcome in single_die_range}

    pdf = {}
    for i in range(1 + modifier, number_of_faces * number_of_dice + modifier + 1):
        if i in single_die_range:
            pdf[i] = die_face_probability
        else:
            pdf[i] = 0
    for i in range(number_of_dice - 1):
        pdf = convolution.convolve(pdf, die_probability_distribution)
    return {key: value for key, value in pdf.items() if value != 0}

def calculate_cdf(outcome_to_probability):
    """Calculate the cumulative distribution function of a dice roll"""
    cumulative_probability = 0
    outcome_to_cumulative_probability = {}
    for outcome, probability in outcome_to_probability.items():
        cumulative_probability += probability
        outcome_to_cumulative_probability[outcome] = cumulative_probability
    return outcome_to_cumulative_probability


def calculate_mean(outcome_to_probability):
    """Calculate the mean dice outcome"""
    outcomes = list(outcome_to_probability.keys())
    probabilities = list(outcome_to_probability.values())
    mean_value = 0
    for i in range(len(outcomes)):
        mean_value += probabilities[i] * outcomes[i]
    mean_value = round(mean_value, 1)
    return mean_value

def display_numerical_results(dice_prompt, outcome_to_cumulative_probability):
    """Display all the numerical insights of the dice roll"""
    max_outcome = max(outcome_to_cumulative_probability.keys())
    min_outcome = min(outcome_to_cumulative_probability.keys())
    
    for outcome, probability in outcome_to_cumulative_probability.items():
        cumulative_probability_percentage = probability * 100
        print(f"P({min_outcome}<=x<={outcome}) = {cumulative_probability_percentage:.3f}%;        P({outcome}<=x<={max_outcome}) = {100 - cumulative_probability_percentage:.3f}%")

def plot_values(prompt, outcome_to_occurrences, mean_value):
    """Plot values given an input dictionary"""
    x_values = list(outcome_to_occurrences.keys())
    y_values = list(outcome_to_occurrences.values())
    x_range = max(x_values) - min(x_values)
    x_tick_increment = math.ceil(x_range / 25) if x_range >= 25 else 1
    print(f"There are {len(x_values)} bars on this histogram")

    matplotlib.pyplot.figure(figsize=(14, 5))
    matplotlib.pyplot.hist(x_values, bins=len(x_values), weights=y_values, color='#D64650', edgecolor='black')
    matplotlib.pyplot.xlabel('Sum')
    matplotlib.pyplot.ylabel('% Occurrence')
    matplotlib.pyplot.title(f'Histogram of Results from {prompt}')
    matplotlib.pyplot.axvline(x=mean_value, label=f"Mean = {mean_value}", color='r')
    matplotlib.pyplot.legend()
    matplotlib.pyplot.xticks(range(min(x_values), max(x_values) + 1, x_tick_increment))
    matplotlib.pyplot.grid(axis='y', linestyle='--', alpha=0.7)
    matplotlib.pyplot.show()

if __name__ == "__main__":
    main()
