import tensorflow as tf
import os

# Convert the model
os.chdir(r"C:\Users\user\Desktop\College_Study\rabboni\rabboni_multi_python_sdk-1.1.0\rabboni_multi_python_sdk-1.1.0")
converter = tf.lite.TFLiteConverter.from_saved_model("accZ_model_lstm") # path to the SavedModel directory

# 設置轉換選項
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]

tflite_model = converter.convert()

# Save the model.
with open('accZ_model_lstm.tflite', 'wb') as f:
  f.write(tflite_model)