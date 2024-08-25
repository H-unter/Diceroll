"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import matplotlib.pyplot
import math
import time
import convolution # custom module for convolution of probability distributions

is_results_displayed = True

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

def calculate_mean(outcome_to_probability):
    """Calculate the mean dice outcome"""
    outcomes = list(outcome_to_probability.keys())
    probabilities = list(outcome_to_probability.values())
    mean_value = 0
    for i in range(len(outcomes)):
        mean_value += probabilities[i] * outcomes[i]
    mean_value = round(mean_value, 1)
    return mean_value

def calculate_cdf(outcome_to_probability):
        """Calculate the cumulative distribution function of a dice roll"""
        cumulative_probability = 0
        outcome_to_cumulative_probability = {}
        for outcome, probability in outcome_to_probability.items():
            cumulative_probability += probability
            outcome_to_cumulative_probability[outcome] = cumulative_probability
        return outcome_to_cumulative_probability

class dice_roll_toolbox:
    def __init__(self, dice_prompt="1d10+3"):
        self.dice_prompt = dice_prompt
        self.number_of_dice, self.number_of_faces, self.modifier = parse_dice_prompt(dice_prompt)
        self.outcome_to_probability = calculate_pdf(self.number_of_faces, self.number_of_dice, self.modifier)
        
        self.min_outcome = min(self.outcome_to_probability.keys())
        self.max_outcome = max(self.outcome_to_probability.keys())
        self.mean_outcome = calculate_mean(self.outcome_to_probability)
        self.outcome_to_cumulative_probability = calculate_cdf(self.outcome_to_probability)

    def output_all_numerical_results(self):
        """Display all the numerical insights of the dice roll"""     
        for outcome, probability in self.outcome_to_cumulative_probability.items():
            cumulative_probability_percentage = probability * 100
            print(f"P({self.min_outcome} <= x <= {outcome}) = {cumulative_probability_percentage:.3f}%;        P({outcome} <= x <= {self.max_outcome}) = {100 - cumulative_probability_percentage:.3f}%")

    def output_select_numerical_results(self, y):
        """Display all the numerical insights of the dice roll"""
        try:
           print(f"P({self.min_outcome} <= x <= {y}) = {self.outcome_to_cumulative_probability[y] * 100:.3f}%;        P({y} <= x <= {self.max_outcome}) = {(1 - self.outcome_to_cumulative_probability[y]) * 100:.3f}%")
        except KeyError:
           print("The value of y is out of range, i should write code to handle this")
        
    def plot_values(self):
        """Plot values given an input dictionary"""
        x_values = list(self.outcome_to_probability.keys())
        y_values = list(self.outcome_to_probability.values())
        x_range = max(x_values) - min(x_values)
        x_tick_increment = math.ceil(x_range / 25) if x_range >= 25 else 1
        print(f"There are {len(x_values)} bars on this histogram")

        matplotlib.pyplot.figure(figsize=(14, 5))
        matplotlib.pyplot.hist(x_values, bins=len(x_values), weights=y_values, color='#D64650', edgecolor='black')
        matplotlib.pyplot.xlabel('Sum')
        matplotlib.pyplot.ylabel('% Occurrence')
        matplotlib.pyplot.title(f'Histogram of Results from {self.dice_prompt}')
        matplotlib.pyplot.axvline(x=self.mean_outcome, label=f"Mean = {self.mean_outcome}", color='r')
        matplotlib.pyplot.legend()
        matplotlib.pyplot.xticks(range(min(x_values), max(x_values) + 1, x_tick_increment))
        matplotlib.pyplot.grid(axis='y', linestyle='--', alpha=0.7)
        matplotlib.pyplot.show()

if __name__ == "__main__":
    # start timer for performance testing
    start_time = time.time()
    dice_roll = dice_roll_toolbox("100d6+1")
    #dice_roll.output_all_numerical_results()
    #dice_roll.output_select_numerical_results(10)
    end_time = time.time() # 2.35599946975708 seconds
    print(f"Execution time: {end_time - start_time} seconds")
    dice_roll.plot_values()
    
    

