"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import matplotlib.pyplot
import math
import time
import convolution # custom module for convolution of probability distributions
import numpy 

is_results_displayed = True

def parse_dice_prompt(dice_prompt):
    """Parse dice prompt and return an object with dice rolls and total offset. eg 2d4+3+4d7+8"""
    dice_prompt = dice_prompt.replace('-', '+-')  # Handle negative offsets
    dice_roll_terms = dice_prompt.split('+')
    
    dice_rolls = []
    total_offset = 0

    for dice_roll_term in dice_roll_terms:
        is_diceroll_term = 'd' in dice_roll_term
        if is_diceroll_term: # dice roll, eg 4d5
            num_dice, num_faces = map(int, dice_roll_term.split('d'))
            dice_rolls.append((num_dice, num_faces))
        else:
            total_offset += int(dice_roll_term)
    return dice_rolls, total_offset

def calculate_pdf(dice_rolls, modifier):
        """Convolve the discrete probability densities https://www.youtube.com/watch?v=IaSGqQa5O-M&ab_channel=3Blue1Brown"""
        pdf = {}
        # Calculate the probability distribution for each dice roll
        max_total_outcome = sum([num_faces*num_dice for (num_dice, num_faces) in dice_rolls]) + modifier
        total_outcome_range = range(1, max_total_outcome + 1)
        pdf = {outcome: 0 for outcome in total_outcome_range}
        is_pdf_initialised = False

        for (number_of_dice, number_of_faces) in dice_rolls:
            die_face_probability = 1 / number_of_faces
            single_die_range = range(1, number_of_faces + 1)
            single_die_pdf = {outcome: die_face_probability for outcome in single_die_range}

            if not is_pdf_initialised:
                pdf = single_die_pdf
                is_pdf_initialised = True
                convolution_count = number_of_dice - 1
            else:
                convolution_count = number_of_dice

            for outcome_index in range(convolution_count):
                pdf = convolution.convolve(pdf, single_die_pdf)

        return {key + modifier: value for key, value in pdf.items() if value != 0} # shift the pdf by the modifier

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
        self.dice_rolls, self.modifier = parse_dice_prompt(dice_prompt)
        self.outcome_to_probability = calculate_pdf(self.dice_rolls, self.modifier)
        
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

        # Calculate the bin edges and bin centers
        bin_edges = numpy.arange(min(x_values) - 0.5, max(x_values) + 1.5, 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        matplotlib.pyplot.figure(figsize=(14, 5))
        matplotlib.pyplot.hist(x_values, bins=bin_edges, weights=y_values, color='#D64650', edgecolor='black')
        matplotlib.pyplot.xlabel('Sum')
        matplotlib.pyplot.ylabel('% Occurrence')
        matplotlib.pyplot.title(f'Histogram of Results from {self.dice_prompt}')
        matplotlib.pyplot.axvline(x=self.mean_outcome, label=f"Mean = {self.mean_outcome}", color='r')
        matplotlib.pyplot.legend()

        # Set x-ticks to the bin centers
        matplotlib.pyplot.xticks(bin_centers[::x_tick_increment], labels=[str(int(center)) for center in bin_centers[::x_tick_increment]])
        
        matplotlib.pyplot.grid(axis='y', linestyle='--', alpha=0.7)
        matplotlib.pyplot.show()

if __name__ == "__main__":
    # start timer for performance testing
    start_time = time.time()
    dice_roll = dice_roll_toolbox("2d6+4d10+1")
    #dice_roll.output_all_numerical_results()
    #dice_roll.output_select_numerical_results(10)
    end_time = time.time() 
    print(f"Execution time: {end_time - start_time} seconds")
    dice_roll.plot_values()
    
    

