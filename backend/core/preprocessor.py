import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import torch
import os
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

class Preprocessor:
    def __init__(self, sam2_checkpoint=None, sam2_config="sam2_hiera_l.yaml"):
        """
        Initializes Preprocessor with MediaPipe and SAM 2.
        """
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True, model_complexity=2)
        
        # Initialize SAM 2
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam2_checkpoint = sam2_checkpoint or os.getenv("SAM2_CHECKPOINT", "sam2_hiera_large.pt")
        self.sam2_config = sam2_config
        
        # We will load the model lazily when first needed to save memory if only pose is requested
        self._sam2_predictor = None

    @property
    def sam2_predictor(self):
        if self._sam2_predictor is None:
            if not os.path.exists(self.sam2_checkpoint):
                raise FileNotFoundError(f"SAM 2 checkpoint not found at {self.sam2_checkpoint}. Please download it first.")
            
            sam2_model = build_sam2(self.sam2_config, self.sam2_checkpoint, device=self.device)
            self._sam2_predictor = SAM2ImagePredictor(sam2_model)
        return self._sam2_predictor

    def get_pose(self, image_path):
        """
        Extracts landmarks from the user image using MediaPipe Pose.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return None
            
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility])
            
        return landmarks

    def get_mask(self, image_path):
        """
        Generates a person mask using SAM 2.
        For VTO, we typically want to segment the person from the background.
        We use a simple point prompt in the center of the image as a heuristic for the person.
        """
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)
        
        self.sam2_predictor.set_image(image_np)
        
        # Simple heuristic: prompt with the center of the image to find the person
        h, w = image_np.shape[:2]
        input_point = np.array([[w // 2, h // 2]])
        input_label = np.array([1]) # Positive prompt
        
        masks, scores, logits = self.sam2_predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=False
        )
        
        # Select the mask with highest score (usually only one since multimask_output=False)
        best_mask = masks[0]
        mask_image = Image.fromarray((best_mask * 255).astype(np.uint8))
        
        return mask_image

    def process(self, image_path):
        """
        Full pre-processing pipeline.
        """
        pose_data = self.get_pose(image_path)
        mask_image = self.get_mask(image_path)
        
        return {
            "pose": pose_data,
            "mask": mask_image
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-image", type=str, required=True)
    parser.add_argument("--checkpoint", type=str, help="Path to SAM 2 checkpoint")
    args = parser.parse_args()
    
    preprocessor = Preprocessor(sam2_checkpoint=args.checkpoint)
    try:
        # Note: This will fail if the checkpoint is not provided/found
        results = preprocessor.process(args.test_image)
        print(f"Successfully processed {args.test_image}")
        print(f"Pose detected: {results['pose'] is not None}")
        print(f"Mask size: {results['mask'].size}")
        
        # Save verification images
        os.makedirs("temp", exist_ok=True)
        results["mask"].save("temp/verification_mask.png")
        print("Saved verification mask to temp/verification_mask.png")
    except Exception as e:
        print(f"Error during pre-processing: {e}")
        print("Note: If SAM 2 weights are missing, pose-only detection still works via mp_pose.")
