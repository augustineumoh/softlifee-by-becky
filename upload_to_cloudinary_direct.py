"""
Upload product images DIRECTLY to Cloudinary with fixed, known public IDs.
Run this ONCE from your local machine — after that the seed command handles
creating the ProductImage DB records automatically on every Railway deploy.

Usage:
    python upload_to_cloudinary_direct.py
"""

import os
import cloudinary
import cloudinary.uploader

# ── CONFIG ────────────────────────────────────────────────────────────────────
CLOUD_NAME = 'dadp7exd8'
API_KEY    = '541571389888287'
API_SECRET = 'PzUCW-9cQfC5gpj6Uyk44-7liO4'

ASSETS_DIR = r'C:\Users\victo\desktop\soft-lifee-frontend\src\assets'
# ─────────────────────────────────────────────────────────────────────────────

cloudinary.config(
    cloud_name = CLOUD_NAME,
    api_key    = API_KEY,
    api_secret = API_SECRET,
    secure     = True,
)

SLUG_TO_IMAGE = {
    'diffuser':                                   'diffuser.jpg',
    '3D-sand-drop':                               'sand drop.jpg',
    'foldable-swivel-mosquito-bat':               'mosquito bat.jpg',
    'ac-cooling-humidifier-fan':                  'Fan.jpg',
    'e-30-camera-fill-light':                     'led light.jpeg',
    'bathroom-organizer':                         'bathroom organizer.jpg',
    'over-the-toilet-organizer-rack':             'over-the-toilet organizer rack.jpg',
    'multifunctional-towel-organizer':            'towel organizer.jpg',
    '5in1-multipurpose-organizer':                'bathroom set.jpeg',
    'flower-vase':                                'flowervase.jpeg',
    'ceramic-cup-set':                            'ceramic cup set.jpeg',
    'storage-basket':                             'storage basket.jpeg',
    'ultra-portable-multi-functional-juicer-cup': 'blender.jpeg',
    'cooking-flipper':                            'cooking fliper.jpg',
    'multifunctional-wall-mounted-trash-can':     'kitchen trash can.jpg',
    'moonlight-lamp':                             'Rechargeable Rotation Moonlight light.jpg',
    'crystal-diamond-led-lamp':                   'diamond led lamp.jpg',
    '360-motion-sensor-light':                    'solar light.jpg',
    'relaxation-chair':                           'relaxation chair.jpg',
    'quick-shoe-wipe':                            'shoe wipe.jpg',
    '3-layers-jewelry-box-with-key':              'jewellery box.jpg',
    'underwear-organizer':                        'underwear organizer.jpg',
    'double-sided-nano-tape':                     'nano tape.jpg',
    'inspirational-wall-stickers':                'wall sticker.jpg',
    'gold-decor-tape':                            'gold decor tape.jpg',
    'vine-leaf-room-decor':                       'vine leaf.jpg',
    'decorative-wall-hooks':                      'wall hooks.jpg',
    'self-adhesive-countertop-film':              'counter film.jpeg',
    'tote-bag':                                   'tote bag.jpg',
    'smart-watch-set':                            'smart watch.jpg',
    'smart-watch-series-8':                       'smart watch series 8.jpg',
    'matte-stanley-tumbler':                      'Matte-stanley-style-tumbler.jpeg',
    'stanley-cup':                                'stanley cup.jpeg',
    'stanley-cup-accessories':                    'Stanley cup accessories.jpg',
    'happy-supply-chain-water-bottle':            'happy supply chain.jpg',
    'laptop-stand':                               'laptop stand.jpg',
    'phone-suction-cup':                          'phone suction.jpg',
    'rgb-phone-led-light':                        'phone led light.jpg',
    'wireless-fill-light-bt-remote-tripod':       'tripod stand.jpg',
    'bubble-gun':                                 'bubble gun.jpg',
    'usb-cigarettes-lighter-mobile-phone-holder': 'usb cigarettes.jpg',
    'fancy-barbie-pen':                           'barbie pen.jpeg',
    'green-stick-mask':                           'stick mask.jpg',
    'star-pimple-patches':                        'pimple patches.jpg',
    'compressed-facial-towel':                    'face towel.jpg',
    'sadoer-ampoules-facial-mask':                'face mask.jpeg',
    'tongue-scrubber':                            'tonuge scraper.jpg',
    'travel-box':                                 'travel box.jpeg',
    'travel-kit':                                 'travel kit.jpg',
    'floral-fruit-fragrance-hand-cream':          'hand cream.jpg',
    'boob-tape':                                  'boobtape.jpg',
    'transparent-boobs-lifter':                   'boops lifter.jpeg',
}


def main():
    ok = fail = skip = 0

    print(f'\nUploading {len(SLUG_TO_IMAGE)} images to Cloudinary…\n')

    for slug, filename in SLUG_TO_IMAGE.items():
        image_path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(image_path):
            print(f'  [MISS] {slug} — file not found: {filename}')
            skip += 1
            continue

        public_id = f'softlifee_products/{slug}'

        try:
            result = cloudinary.uploader.upload(
                image_path,
                public_id    = public_id,
                overwrite    = True,
                resource_type = 'image',
            )
            print(f'  [OK]   {slug} -> {result["public_id"]}')
            ok += 1
        except Exception as e:
            print(f'  [ERR]  {slug} — {e}')
            fail += 1

    print(f'\nDone. OK: {ok}  |  Skipped: {skip}  |  Failed: {fail}')
    if fail == 0 and skip == 0:
        print('\nAll images are now on Cloudinary with public IDs:')
        print('  softlifee_products/<slug>')
        print('\nThe seed command will use these IDs automatically on Railway deploys.')


if __name__ == '__main__':
    main()
