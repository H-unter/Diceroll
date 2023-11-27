"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import random

# prompt = input("Enter Dice: ")  # 2d6+1
prompt = "2d6+1"
number_of_dice = int(prompt.split('d')[0])
number_of_faces = int(prompt.split('+')[0][-1])
modifier = int(prompt.split('+')[1][0])

minimum_outcome = number_of_dice + modifier
maximum_outcome = number_of_dice * number_of_faces + modifier

print(f"for: {number_of_dice}d{number_of_faces}+{modifier}")
outcome_to_occurrences = {}
for i in range(minimum_outcome, maximum_outcome + 1):
    outcome_to_occurrences[i] = 0

for i in range(0, 10000):
    result = random.randint(1, number_of_faces) + random.randint(1, number_of_faces) + modifier
    outcome_to_occurrences[result] += 1

print(outcome_to_occurrences)
