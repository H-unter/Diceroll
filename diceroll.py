"""
Hunter Kruger-Ilingworth | Dice roll application
"""

prompt = input("Enter Dice: ")  # 2d6+1
dice_number = int(prompt.split('d')[0])
dice_type = int(prompt.split('+')[0][-1])
modifier = int(prompt.split('+')[1][0])

print(f"for: {dice_number}d{dice_type}+{modifier}")

chance = (1 / dice_type) * 100
for i in range(1, dice_type+1):
    outcome = i + modifier
    print(f"Chance of getting {outcome} = {chance:2f}%")
