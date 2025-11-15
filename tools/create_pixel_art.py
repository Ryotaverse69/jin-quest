#!/usr/bin/env python3
"""
写真からレトロゲーム風のドット絵を生成するツール
"""

from PIL import Image, ImageEnhance, ImageFilter
import sys

def create_retro_pixel_art(input_path, output_path, target_width=240, colors=32):
    """
    写真をレトロゲーム風のドット絵に変換

    Args:
        input_path: 入力画像のパス
        output_path: 出力画像のパス
        target_width: ドット絵の幅（ピクセル）
        colors: 使用する色数（少ないほどレトロ風）
    """
    print(f"画像を読み込んでいます: {input_path}")
    img = Image.open(input_path)

    # 1. アスペクト比を維持しながらリサイズ
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio)
    print(f"ドット絵サイズ: {target_width}x{target_height}px")

    # 2. 小さいサイズにリサイズ（LANCZOSで高品質に）
    img_small = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # 3. コントラストを強調（レトロゲーム風）
    enhancer = ImageEnhance.Contrast(img_small)
    img_small = enhancer.enhance(1.3)

    # 4. 彩度を少し上げる（レトロゲーム風の鮮やかな色）
    enhancer = ImageEnhance.Color(img_small)
    img_small = enhancer.enhance(1.2)

    # 5. 色数を制限（パレット化）してレトロ風に
    print(f"色数を{colors}色に制限しています...")
    img_palette = img_small.convert('P', palette=Image.ADAPTIVE, colors=colors)

    # 6. RGBに戻す
    img_pixel = img_palette.convert('RGB')

    # 7. 軽いシャープフィルタを適用（ドットをくっきりさせる）
    img_pixel = img_pixel.filter(ImageFilter.SHARPEN)

    # 8. ゲーム画面サイズ（1920x1080）に最近傍補間で拡大
    # 画面全体を覆うように拡大（クロップあり）
    screen_width = 1920
    screen_height = 1080
    screen_aspect = screen_width / screen_height
    pixel_aspect = target_width / target_height

    if pixel_aspect > screen_aspect:
        # 画像が横長の場合、高さを基準にして横をクロップ
        final_height = screen_height
        final_width = int(screen_height * pixel_aspect)
    else:
        # 画像が縦長の場合、幅を基準にして縦をクロップ
        final_width = screen_width
        final_height = int(screen_width / pixel_aspect)

    print(f"最終サイズに拡大: {final_width}x{final_height}px")
    # 最近傍補間（NEAREST）でピクセル感を保持
    img_final = img_pixel.resize((final_width, final_height), Image.Resampling.NEAREST)

    # 9. 画面サイズのキャンバスを作成して中央配置（クロップ）
    canvas = Image.new('RGB', (screen_width, screen_height), (0, 0, 0))
    x_offset = (screen_width - final_width) // 2
    y_offset = (screen_height - final_height) // 2

    # クロップして画面サイズにぴったり合わせる
    if final_width > screen_width or final_height > screen_height:
        # クロップが必要な場合
        crop_x = max(0, -x_offset)
        crop_y = max(0, -y_offset)
        crop_width = min(final_width, screen_width)
        crop_height = min(final_height, screen_height)
        img_cropped = img_final.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
        canvas.paste(img_cropped, (max(0, x_offset), max(0, y_offset)))
    else:
        canvas.paste(img_final, (x_offset, y_offset))

    # 10. 保存
    print(f"保存しています: {output_path}")
    canvas.save(output_path, quality=95)
    print("完了！")

if __name__ == "__main__":
    input_image = "assets/ui/jid_headquarters_bg.jpg"
    output_image = "assets/ui/jid_headquarters_pixel_art.png"

    # スーパーファミコン風の設定
    # 幅240px = SFC解像度の約1/2（程よいドット感）
    # 32色 = レトロゲーム風のカラーパレット
    create_retro_pixel_art(
        input_image,
        output_image,
        target_width=240,  # ドット絵の幅
        colors=32  # 使用色数（16-64が良い感じ）
    )
