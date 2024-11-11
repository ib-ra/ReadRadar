import requests
import pandas as pd
import time  # Import the time module
from PIL import Image, ImageDraw
from io import BytesIO

def fetch_and_process_radar_image(image_url, center_point, radius, values_to_delete, threshold):
    # Extract city from the URL
    city_name = extract_city_name(image_url)
    
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
    count_red_below_5 = sum(1 for r, g, b in filtered_rgb_values if r < threshold)
    count_blue_below_5 = sum(1 for r, g, b in filtered_rgb_values if b < threshold)
    count_green_below_5 = sum(1 for r, g, b in filtered_rgb_values if g < threshold)

    # Return city name and pixel counts
    return city_name, count_red_below_5, count_green_below_5, count_blue_below_5

def extract_city_name(image_url):
    # Check the image URL for the city code and return the corresponding city name
    city_mapping = {
        'afy': "Afyonkarahisar", 'ank': "Ankara", 'ant': "Antalya", 'blk': "Balıkesir", 'brs': "Bursa",
        'erz': "Erzurum", 'gzt': "Gaziantep", 'hty': "Hatay", 'ist': "İstanbul", 'izm': "İzmir",
        'krm': "Karaman", 'mob': "Kilis", 'mgl': "Muğla", 'smn': "Samsun", 'svs': "Sivas", 'srf': "Şanlıurfa",
        'trb': "Trabzon", 'zng': "Zonguldak"
    }
    for code, city in city_mapping.items():
        if code in image_url:
            return city
    return "Unknown City"

def crop_image_circle(img, center, radius):
    # Create a mask image with the same size as the original image
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)

    # Draw the circle on the mask
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=255)

    # Apply the mask
    img_cropped = Image.new('RGB', img.size)
    img_cropped.paste(img, mask=mask)

    # Crop to the circle's bounding box
    left = max(0, center[0] - radius)
    upper = max(0, center[1] - radius)
    right = min(img.size[0], center[0] + radius)
    lower = min(img.size[1], center[1] + radius)

    return img_cropped.crop((left, upper, right, lower))

def process_multiple_urls(urls, center_point, radius, values_to_delete, threshold):
    results = []  # List to store the results
    # Loop through all URLs and process each one
    for image_url in urls:
        city_name, red_count, green_count, blue_count = fetch_and_process_radar_image(
            image_url, center_point, radius, values_to_delete, threshold
        )
        
        # Store the results in a list
        results.append({
            'City': city_name,
            'Light Rain': red_count,
            'Moderate Rain': blue_count,
            'Heavy Rain': green_count
        })
    
    return results

def save_to_csv(results, filename):
    # Create a DataFrame from the results
    df = pd.DataFrame(results)
    
    # Save to CSV file
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    
    return df

def show_pivot(df):
    # Pivot the data to have colors as columns
    pivot_df = df.melt(id_vars=["City"], value_vars=["Light Rain", "Moderate Rain", "Heavy Rain"],
                       var_name="Rain Intensity", value_name="Count")
    pivot_table = pivot_df.pivot(index="City", columns="Rain Intensity", values="Count")
    
    print("\nPivot Table:")
    print(pivot_table)

# Function to read CSV and print the time taken
def read_csv_and_time(filename):
    start_time = time.time()  # Start the timer
    df = pd.read_csv(filename)
    end_time = time.time()  # End the timer

    # Calculate and print the time taken to read the file
    print(f"Time taken to read the CSV file: {end_time - start_time:.4f} seconds")
    
    return df

def main():
    # List of image URLs for different cities
    image_urls = [
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/afy/afyppi15.jpg',  # Afyonkarahisar
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/ank/ankppi15.jpg',  # Ankara
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/ant/antppi15.jpg',  # Antalya
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/blk/blkppi15.jpg',  # Balıkesir
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/brs/brsppi15.jpg',  # Bursa
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/erz/erzppi15.jpg',  # Erzurum
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/gzt/gztppi15.jpg',  # Gaziantep
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/hty/htyppi15.jpg',  # Hatay
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/ist/istppi15.jpg',  # İstanbul
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/izm/izmppi15.jpg',  # İzmir
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/krm/krmppi15.jpg',  # Karaman
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/mob/mobppi15.jpg',  # Kilis
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/mgl/mglppi15.jpg',  # Muğla
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/smn/smnppi15.jpg',  # Samsun
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/svs/svsppi15.jpg',  # Sivas
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/srf/srfppi15.jpg',  # Şanlıurfa
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/trb/trbppi15.jpg',  # Trabzon
        'https://www.mgm.gov.tr/FTPDATA/uzal/radar/zng/zngppi15.jpg'   # Zonguldak
    ]
    
    # Configuration
    center_point = (360, 360)  # Example center of the radar image
    radius = 360  # Example radius of the circle for cropping
    values_to_delete = [(0, 0, 0), (148, 201, 255), (255, 255, 217)]  # Colors to delete
    threshold = 5  # Threshold for component values

    # Process the list of image URLs
    results = process_multiple_urls(image_urls, center_point, radius, values_to_delete, threshold)
    
    # Save results to CSV
    filename = 'radar_pixel_counts.csv'
    df = save_to_csv(results, filename)
    
    # Show pivot table
    show_pivot(df)
    
    # Read the CSV file and measure the time taken
    read_csv_and_time(filename)

if __name__ == "__main__":
    main()
