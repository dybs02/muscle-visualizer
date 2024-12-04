import pygame
import pandas as pd
import numpy as np

# Initialize Pygame
pygame.init()

# Screen Dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Muscle Activation Visualization")

# Load the Arm Image
arm_image = pygame.image.load("arm_image.png")  # Replace with your image file path
arm_image = pygame.transform.scale(arm_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load the Muscle Data (CSV file)
data = pd.read_csv("muscle_data.csv")  # Replace with the correct CSV file path
time = data["Time (ms)"]
biceps_signal = data["Biceps Signal"]
triceps_signal = data["Triceps Signal"]

# Normalize Muscle Signals
biceps_signal = (biceps_signal - biceps_signal.min()) / (biceps_signal.max() - biceps_signal.min())
triceps_signal = (triceps_signal - triceps_signal.min()) / (triceps_signal.max() - triceps_signal.min())

# Muscle Regions (Example Rectangles)
# These coordinates depend on your arm image layout
muscle_regions = {
    "biceps": pygame.Rect(200, 150, 150, 200),  # Example region for biceps
    "triceps": pygame.Rect(450, 150, 150, 200),  # Example region for triceps
}

# Define Colors
REST_COLOR = (0, 255, 0)  # Green for rest
ACTIVE_COLOR = (255, 0, 0)  # Red for active
BACKGROUND_COLOR = (0, 0, 0)

# Helper Function to Compute Color Intensity
def get_color(intensity, base_color=ACTIVE_COLOR):
    """Returns a color scaled by intensity."""
    r, g, b = base_color
    return (int(r * intensity), int(g * intensity), int(b * intensity))

# Main Loop
clock = pygame.time.Clock()
running = True
index = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the Screen
    screen.fill(BACKGROUND_COLOR)

    # Draw the Arm Image
    screen.blit(arm_image, (0, 0))

    # Update Muscle Highlights
    if index < len(time):
        # Get Current Intensity
        biceps_intensity = biceps_signal[index]
        triceps_intensity = triceps_signal[index]

        # Highlight Biceps
        biceps_color = get_color(biceps_intensity)
        pygame.draw.rect(screen, biceps_color, muscle_regions["biceps"])

        # Highlight Triceps
        triceps_color = get_color(triceps_intensity)
        pygame.draw.rect(screen, triceps_color, muscle_regions["triceps"])

        # Increment Frame Index
        index += 1
    else:
        # Loop the animation if desired
        index = 0

    # Update Display
    pygame.display.flip()

    # Control Frame Rate
    clock.tick(30)  # 30 FPS

# Quit Pygame
pygame.quit()
