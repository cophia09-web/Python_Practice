import io
import torch
from torchvision import models, transforms
from PIL import Image
from typing import Tuple

# Завантажуємо модель глобально один раз
weights = models.MobileNet_V2_Weights.DEFAULT
model = models.mobilenet_v2(weights=weights)
model.eval()

# Трансформації зображення (розміри та нормалізація)
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def classify_image(image_bytes: bytes) -> Tuple[str, float]:
    """Синхронна класифікація. Виконується ТІЛЬКИ поза event loop."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)

    # Використовуємо torch.no_grad() для економії пам'яті
    with torch.no_grad():
        output = model(input_batch)

    # Отримуємо ймовірності
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    confidence, class_idx = torch.max(probabilities, dim=0)
    class_name = weights.meta["categories"][class_idx.item()]

    return class_name, confidence.item()