from core.prediction_functions import predict_JP, predict_dichotomy

user_input = "guide events through careful planning and choice"
label, probability = predict_dichotomy(27, user_input, "J/P")

print(label, probability)

user_input = "guide events through careful planning and choice"
label, probability = predict_JP(27, user_input)

print(label, probability)