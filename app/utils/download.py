import os
import requests
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from .logger import log

BASE_URL = os.getenv('MEDIA_DIR')

def get_save_path(post_id):
    today_str = datetime.now().strftime('%Y%m%d')
    save_dir = os.path.join(BASE_URL, f'{today_str}/{post_id}')
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def download_file(url, save_dir):
    try:
        file_name = url.split('/')[-1]
        os.makedirs(f'{save_dir}/videos', exist_ok=True)
        os.makedirs(f'{save_dir}/images', exist_ok=True)

        if '.mp4' in file_name:  # 视频
            video_name = file_name.split('.')[0]
            save_file = os.path.join(f'{save_dir}/videos', f'{video_name}.mp4')
        else:
            img_name = file_name.split('!')[0]
            save_file = os.path.join(f'{save_dir}/images', f'{img_name}.webp')

        response = requests.get(url, stream=True, timeout=1000)
        response.raise_for_status()

        with open(save_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        log.info(f'下载成功: {save_file}')

        return save_file

    except Exception as e:
        log.error(f'下载失败: {e}')
        return f"下载失败: {url} -> {e}"


def transform_webp_png(img_path):
    try:
        img = Image.open(img_path)
        img.save(f'{img_path.replace('.webp', '')}.png')
        log.success(f'转换成功: {img_path}')
    except Exception as e:
        log.error(f'转换失败: {str(e)}')


def download_media(note_id: str, media_urls: list):
    save_dir = get_save_path(note_id)
    results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(download_file, url, save_dir)
            for i, url in enumerate(media_urls)
        ]
        for f in futures:
            results.append(f.result())

    for file_path in results:
        if '.webp' in file_path:
            transform_webp_png(file_path)

    return results
