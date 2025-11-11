from prediction_functions import predict_JP

user_input = "guide events through careful planning and choice"
label, probability = predict_JP(27, user_input)

print(label, probability)