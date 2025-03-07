import codecs
import unittest
from fastapi.testclient import TestClient
from main import app  
import os
import httpx

client = TestClient(app)

class TestApp(unittest.TestCase):

    # def test_predict_from_taken_photo(self):
    #     # Test de la fonction predict_from_taken_photo
    #     response = client.get("/predict_from_taken_photo")
    #     self.assertEqual(response.status_code, 200)
    #     if "message" in response.json():
    #         self.assertIn(response.json()["message"], ["Aucun visage détecté de face dans l'image", "Plusieurs visages sont détectés. Veuillez mettre une image d'un seul visage"])
    #     else:
    #         self.assertIn("predicted_emotion", response.json())

    def test_predict_from_uploaded_image(self):
        # Test de la fonction predict_from_uploaded_image
        with open("app/test_image.png", "rb") as file:
            response = client.post("/predict_from_uploaded_image", files={"file": file})
        self.assertEqual(response.status_code, 200)
        if "message" in response.json():
            self.assertIn(response.json()["message"], ["Aucun visage détecté de face dans l'image", "Plusieurs visages sont détectés. Veuillez mettre une image d'un seul visage"])
        else:
            self.assertIn("predicted_emotion", response.json())

    def test_front_root(self):
        # Test de la fonction front_root
        response = client.get("/frontend")
        self.assertEqual(response.status_code, 200)
        with codecs.open("app/frontend.html", 'r', 'utf-8') as f:
            html_content = f.read()
        self.assertEqual(response.content.decode('utf-8'), html_content)

    def test_metrics_machine_learning(self):
        # Test de la fonction metrics_machine_learning
        response = client.get("/metrics_machine_learning")
        self.assertEqual(response.status_code, 200)

    def test_read_root(self):
        # Test de la fonction read_root
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        with codecs.open("app/presentation.html", 'r', 'utf-8') as f:
            html_content = f.read()
        self.assertEqual(response.content.decode('utf-8'), html_content)

# if __name__ == '__main__':
#     unittest.main()
