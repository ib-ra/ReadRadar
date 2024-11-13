import requests
import pandas as pd
import time
from PIL import Image, ImageDraw
from io import BytesIO
from datetime import datetime


def create_template_dataframe():
    index = pd.MultiIndex(levels=[[], []], codes=[[], []], names=['City', 'Rain Type'])
    df = pd.DataFrame(index=index)
    return df

def fetch_and_process_radar_image(image_url, center_point, radius, values_to_delete, threshold):
    city_name = extract_city_name(image_url)
    response = requests.get(image_url)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))

    cropped_img = crop_image_circle(img, center_point, radius)
    rgb_values = list(cropped_img.getdata())
    filtered_rgb_values = [rgb for rgb in rgb_values if rgb not in values_to_delete]

    count_red_below_5 = sum(1 for r, g, b in filtered_rgb_values if r < threshold)
    count_blue_below_5 = sum(1 for r, g, b in filtered_rgb_values if b < threshold)
    count_green_below_5 = sum(1 for r, g, b in filtered_rgb_values if g < threshold)

    return city_name, count_red_below_5, count_green_below_5, count_blue_below_5

def extract_city_name(image_url):
    city_mapping = {
        'afy': "Afyonkarahisar", 'ank': "Ankara", 'ant': "Antalya", 'blk': "Balikesir", 'brs': "Bursa",
        'erz': "Erzurum", 'gzt': "Gaziantep", 'hty': "Hatay", 'ist': "Istanbul", 'izm': "Izmir",
        'krm': "Karaman", 'mob': "Kilis", 'mgl': "Mugla", 'smn': "Samsun", 'svs': "Sivas", 'srf': "Sanliurfa",
        'trb': "Trabzon", 'zng': "Zonguldak"
    }
    for code, city in city_mapping.items():
        if code in image_url:
            return city
    return "Unknown City"

def crop_image_circle(img, center, radius):
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=255)

    img_cropped = Image.new('RGB', img.size)
    img_cropped.paste(img, mask=mask)

    left = max(0, center[0] - radius)
    upper = max(0, center[1] - radius)
    right = min(img.size[0], center[0] + radius)
    lower = min(img.size[1], center[1] + radius)

    return img_cropped.crop((left, upper, right, lower))

def process_multiple_urls(urls, center_point, radius, values_to_delete, threshold):
    # Subtraction noise
    noise_heavy = 3000
    noise_mod = 5000
    noise_light = 5000
    
    results = []
    for image_url in urls:
        city_name, red_count, green_count, blue_count = fetch_and_process_radar_image(
            image_url, center_point, radius, values_to_delete, threshold
        )
        
        # Subtract noise values and ensure they don't go negative
        light_rain = max(0, red_count - noise_light)
        moderate_rain = max(0, blue_count - noise_mod)
        heavy_rain = max(0, green_count - noise_heavy)
        
        results.append({
            'City': city_name,
            'Light Rain': light_rain,
            'Moderate Rain': moderate_rain,
            'Heavy Rain': heavy_rain
        })
    return results

def append_to_dataframe(df, results):
    new_data = []
    for entry in results:
        for rain_type in ['Light Rain', 'Moderate Rain', 'Heavy Rain']:
            new_data.append([entry['City'], rain_type, entry[rain_type]])

    new_column_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M")}'
    new_df = pd.DataFrame(new_data, columns=['City', 'Rain Type', new_column_name])
    new_df.set_index(['City', 'Rain Type'], inplace=True)

    return df.join(new_df, how='outer', rsuffix='_new')

def save_dataframe(df, filename="rainfall_data.csv"):
    df.to_csv(filename)

def main():
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

    center_point = (360, 360)
    radius = 360
    values_to_delete = [(0, 0, 0), (148, 201, 255), (255, 255, 217)]
    threshold = 5

    df = create_template_dataframe()

    nmbr = 1
    while True:
        results = process_multiple_urls(image_urls, center_point, radius, values_to_delete, threshold)
        df = append_to_dataframe(df, results)
        save_dataframe(df)

        print(f"DataFrame updated... {nmbr}")
        nmbr += 1
        time.sleep(20)  # wait in seconds

if __name__ == "__main__":
    main()