def clean_images_response(images: list):
    result = []

    for i, img in enumerate(images):
        if img.get("key") and img["key"] != 'images/':
            result.append({'id': i, 'url': img['url'], 'alt': 'gallery'})

    return result