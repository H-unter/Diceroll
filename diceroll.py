"""
Hunter Kruger-Ilingworth | Dice roll application
"""

prompt = input("Enter Dice: ") #2d6+1
dice_number = prompt.split('d')[0]
dice_type = prompt.split('d')[1][0]
modifier = prompt.split('d')[1][2]

print(f"for: {dice_number}d{dice_type}+{modifier}")
