import requests
from PIL import Image, ImageDraw
from io import BytesIO

def fetch_and_process_radar_image(image_url, center_point, radius, values_to_delete):
    """
    Fetches a radar image, crops it to a circle, and analyzes RGB values
    
    Args:
        image_url (str): URL of the radar image
        center_point (tuple): (x, y) coordinates for the center of the circle
        radius (int): Radius of the circle to crop
        values_to_delete (list): List of RGB tuples to filter out
        
    Returns:
        tuple: Counts of pixels with RGB values below 5
    """
    try:
        # Fetch the image
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        img = Image.open(BytesIO(response.content))
        
        # Crop the image in a circle
        cropped_img = crop_image_circle(img, center_point, radius)
        
        # Process the RGB values
        rgb_values = list(cropped_img.getdata())
        filtered_rgb_values = [rgb for rgb in rgb_values if rgb not in values_to_delete]
        
        # Count pixels where components are below 5
        count_red_below_5 = sum(1 for r, g, b in filtered_rgb_values if r < 5)
        count_green_below_5 = sum(1 for r, g, b in filtered_rgb_values if g < 5)
        count_blue_below_5 = sum(1 for r, g, b in filtered_rgb_values if b < 5)
        
        return count_red_below_5, count_green_below_5, count_blue_below_5
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def crop_image_circle(img, center, radius):
    """
    Crops an image to a circle using a mask
    
    Args:
        img (PIL.Image): Input image
        center (tuple): (x, y) coordinates of the circle center
        radius (int): Radius of the circle
        
    Returns:
        PIL.Image: Cropped circular image
    """
    # Create a mask image with the same size as the original image
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw the circle on the mask
    draw.ellipse((
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius
    ), fill=255)
    
    # Apply the mask
    img_cropped = Image.new('RGB', img.size)
    img_cropped.paste(img, mask=mask)
    
    # Crop to the circle's bounding box
    left = max(0, center[0] - radius)
    upper = max(0, center[1] - radius)
    right = min(img.size[0], center[0] + radius)
    lower = min(img.size[1], center[1] + radius)
    
    return img_cropped.crop((left, upper, right, lower))

def main():
    # Configuration
    image_url = 'https://www.mgm.gov.tr/FTPDATA/uzal/radar/hty/htyppi15.jpg'
    center_point = (360, 360)
    radius = 360
    values_to_delete = [(0, 0, 0), (148, 201, 255), (255, 255, 217)]
    
    # Process the image
    results = fetch_and_process_radar_image(image_url, center_point, radius, values_to_delete)
    
    if results:
        red_count, green_count, blue_count = results
        print(f'Number of pixels with red component lower than 5: {red_count}')
        print(f'Number of pixels with green component lower than 5: {green_count}')
        print(f'Number of pixels with blue component lower than 5: {blue_count}')

if __name__ == "__main__":
    main()