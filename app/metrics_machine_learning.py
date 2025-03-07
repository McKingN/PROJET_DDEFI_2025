from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
from prometheus_client import Gauge
import os
from utils.predict_by_Img_path import predict_emotion


# Créez des jauges pour suivre les métriques
f1_score_gauge = Gauge('model_f1_score', 'The F1 Score of the model')
accuracy_gauge = Gauge('model_accuracy', 'The accuracy of the model')
precision_gauge = Gauge('model_precision', 'The precision of the model')
recall_gauge = Gauge('model_recall', 'The recall of the model')

async def main():
    emotion_list = ["angry", "disgusted", "fearful", "happy", "neutral", "sad", "surprised"]
        
    true_values = []
    predictions = []    

    
    for emotion in emotion_list:
        emotion_folder = f"datas/test_final/{emotion}"
        
        # Check if the folder exists
        if os.path.exists(emotion_folder):
            # List all files in the folder
            files = os.listdir(emotion_folder)

            # Iterate through each file
            for file in files:
                file_path = os.path.join(emotion_folder, file)

                # Use await within an asynchronous context
                result = await predict_emotion(file_path)
                prediction = result["predicted_emotion"]
  

                # La vraie valeur est le nom du sous-dossier
                true_values.append(emotion)
                predictions.append(prediction)

    # Calculez les métriques
    f1 = f1_score(true_values, predictions, average='macro')
    accuracy = accuracy_score(true_values, predictions)
    # Use zero_division parameter to handle warnings
    precision = precision_score(true_values, predictions, average='macro', zero_division=1)
    recall = recall_score(true_values, predictions, average='macro', zero_division=1)

    # Mettez à jour les jauges avec les nouvelles valeurs
    f1_score_gauge.set(f1)
    accuracy_gauge.set(accuracy)
    precision_gauge.set(precision)
    recall_gauge.set(recall)



