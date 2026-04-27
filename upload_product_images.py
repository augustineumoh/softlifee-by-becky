"""
Upload product images to the backend (which stores them on Cloudinary).

Usage:
    python upload_product_images.py

Edit the three config variables at the top before running.
"""

import os
import requests

# ── CONFIG ────────────────────────────────────────────────────────────────────
BACKEND_URL  = 'https://web-production-40018.up.railway.app'   # no trailing slash
ADMIN_EMAIL  = 'victoriaaugustineumoh@gmail.com'
ADMIN_PASS   = 'SoftLifee2026!'    # fill in your admin password

# Path to the frontend assets folder on your machine
ASSETS_DIR = r'C:\Users\victo\desktop\soft-lifee-frontend\src\assets'
# ─────────────────────────────────────────────────────────────────────────────

# product slug  →  image filename (relative to ASSETS_DIR)
SLUG_TO_IMAGE = {
    'diffuser':                                 'diffuser.jpg',
    '3D-sand-drop':                             'sand drop.jpg',
    'foldable-swivel-mosquito-bat':             'mosquito bat.jpg',
    'ac-cooling-humidifier-fan':                'Fan.jpg',
    'e-30-camera-fill-light':                   'led light.jpeg',
    'bathroom-organizer':                       'bathroom organizer.jpg',
    'over-the-toilet-organizer-rack':           'over-the-toilet organizer rack.jpg',
    'multifunctional-towel-organizer':          'towel organizer.jpg',
    '5in1-multipurpose-organizer':              'bathroom set.jpeg',
    'flower-vase':                              'flowervase.jpeg',
    'ceramic-cup-set':                          'ceramic cup set.jpeg',
    'storage-basket':                           'storage basket.jpeg',
    'ultra-portable-multi-functional-juicer-cup': 'blender.jpeg',
    'cooking-flipper':                          'cooking fliper.jpg',
    'multifunctional-wall-mounted-trash-can':   'kitchen trash can.jpg',
    'moonlight-lamp':                           'Rechargeable Rotation Moonlight light.jpg',
    'crystal-diamond-led-lamp':                 'diamond led lamp.jpg',
    '360-motion-sensor-light':                  'solar light.jpg',
    'relaxation-chair':                         'relaxation chair.jpg',
    'quick-shoe-wipe':                          'shoe wipe.jpg',
    '3-layers-jewelry-box-with-key':            'jewellery box.jpg',
    'underwear-organizer':                      'underwear organizer.jpg',
    'double-sided-nano-tape':                   'nano tape.jpg',
    'inspirational-wall-stickers':              'wall sticker.jpg',
    'gold-decor-tape':                          'gold decor tape.jpg',
    'vine-leaf-room-decor':                     'vine leaf.jpg',
    'decorative-wall-hooks':                    'wall hooks.jpg',
    'self-adhesive-countertop-film':            'counter film.jpeg',
    'tote-bag':                                 'tote bag.jpg',
    'smart-watch-set':                          'smart watch.jpg',
    'smart-watch-series-8':                     'smart watch series 8.jpg',
    'matte-stanley-tumbler':                    'Matte-stanley-style-tumbler.jpeg',
    'stanley-cup':                              'stanley cup.jpeg',
    'stanley-cup-accessories':                  'Stanley cup accessories.jpg',
    'happy-supply-chain-water-bottle':          'happy supply chain.jpg',
    'laptop-stand':                             'laptop stand.jpg',
    'phone-suction-cup':                        'phone suction.jpg',
    'rgb-phone-led-light':                      'phone led light.jpg',
    'wireless-fill-light-bt-remote-tripod':     'tripod stand.jpg',
    'bubble-gun':                               'bubble gun.jpg',
    'usb-cigarettes-lighter-mobile-phone-holder': 'usb cigarettes.jpg',
    'fancy-barbie-pen':                         'barbie pen.jpeg',
    'green-stick-mask':                         'stick mask.jpg',
    'star-pimple-patches':                      'pimple patches.jpg',
    'compressed-facial-towel':                  'face towel.jpg',
    'sadoer-ampoules-facial-mask':              'face mask.jpeg',
    'tongue-scrubber':                          'tonuge scraper.jpg',
    'travel-box':                               'travel box.jpeg',
    'travel-kit':                               'travel kit.jpg',
    'floral-fruit-fragrance-hand-cream':        'hand cream.jpg',
    'boob-tape':                                'boobtape.jpg',
    'transparent-boobs-lifter':                 'boops lifter.jpeg',
}


def login(session):
    resp = session.post(
        f'{BACKEND_URL}/api/v1/auth/login/',
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASS},
        timeout=30,
    )
    resp.raise_for_status()
    token = resp.json()['tokens']['access']
    session.headers['Authorization'] = f'Bearer {token}'
    print(f'  Logged in as {ADMIN_EMAIL}')
    return session


def upload_image(session, slug, image_path):
    url = f'{BACKEND_URL}/api/v1/products/admin/{slug}/images/'
    with open(image_path, 'rb') as f:
        filename = os.path.basename(image_path)
        resp = session.post(
            url,
            files={'image': (filename, f)},
            data={'is_primary': 'true', 'alt_text': slug.replace('-', ' ').title()},
            timeout=60,
        )
    if resp.status_code == 201:
        print(f'  [OK]   {slug}')
    elif resp.status_code == 404:
        print(f'  [SKIP] {slug} — product not found on server')
    else:
        print(f'  [ERR]  {slug} — {resp.status_code}: {resp.text[:120]}')


def main():
    if not ADMIN_PASS:
        print('ERROR: fill in ADMIN_PASS at the top of this script before running.')
        return

    session = requests.Session()

    print('\n── Logging in…')
    try:
        login(session)
    except Exception as e:
        print(f'Login failed: {e}')
        return

    print(f'\n── Uploading {len(SLUG_TO_IMAGE)} product images…\n')
    missing = []
    for slug, filename in SLUG_TO_IMAGE.items():
        image_path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(image_path):
            print(f'  [MISS] {slug} — file not found: {filename}')
            missing.append((slug, filename))
            continue
        upload_image(session, slug, image_path)

    print('\n── Done.')
    if missing:
        print(f'\nMissing files ({len(missing)}):')
        for slug, fn in missing:
            print(f'  {slug}: {fn}')


if __name__ == '__main__':
    main()
