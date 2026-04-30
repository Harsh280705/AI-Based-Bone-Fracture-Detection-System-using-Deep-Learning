from tensorflow.keras.models import load_model

# Load the model
model = load_model('weights/ResNet50_BodyParts.h5')

# Print model summary
model.summary()
