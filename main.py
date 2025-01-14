from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import os
import sys
import configparser

required_files = ["config.ini", "Leica.png"]
for file in required_files:
    if not os.path.isfile(file):
        print("请先完整解压后再运行！！！")
        print("缺少文件 config.ini 或 Leica.png")
        input("请按回车键继续. . .")
        sys.exit(0)

print("╔╗──╔═══╗╔══╗╔══╗╔══╗")
print("║║──║╔══╝╚╗╔╝║╔═╝║╔╗║")
print("║║──║╚══╗─║║─║║──║╚╝║")
print("║║──║╔══╝─║║─║║──║╔╗║")
print("║╚═╗║╚══╗╔╝╚╗║╚═╗║║║║")
print("╚══╝╚═══╝╚══╝╚══╝╚╝╚╝")
print("小米徕卡水印转高斯模糊V1.0 by 酷安@Mr_Bocchi")
print()

config = configparser.ConfigParser()
config.read('./config.ini')

fix = int(config['settings']['photo_edge'])
fix2 = int(config['settings']['logo_edge'])
alpha_text = float(config['settings']['alpha_text'])

hex_color_1 = config['leica_color']['leica_color_1']
hex_color_2 = config['leica_color']['leica_color_2']
hex_color_3 = config['leica_color']['leica_color_3']

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

leica_color_1 = hex_to_rgb(hex_color_1)
leica_color_2 = hex_to_rgb(hex_color_2)
leica_color_3 = hex_to_rgb(hex_color_3)

# 输入和输出目录
input_dir = "./input"
output_dir = "./output"
if not os.path.exists(input_dir):
    os.makedirs(input_dir)
    print("请先将原图放入 input 文件夹后再执行该脚本。")
    sys.exit(0)
os.makedirs(output_dir, exist_ok=True)

logo = Image.open('./Leica.png')

leica_var = False
while True:
    leica_choice = input("是否需要红色徕卡Logo？0不需要 1需要（默认0）：")
    if leica_choice == '1':
        leica_var = True
        print("提示：使用红色Logo请务必放入原图，否则Logo定位大概率会错位或失败！")
        break
    elif leica_choice == '0':
        break
    else:
        #os.system("cls" if os.name == "nt" else "clear")
        #continue
        break

print("图像处理中，请耐心等待...")

# 遍历输入目录中的所有图片
for filename in os.listdir(input_dir):
    input_path = os.path.join(input_dir, filename)

    # 检查文件是否为图像
    if not filename.lower().endswith((".jpg", ".jpeg")):
        continue

    # 打开图像
    img = Image.open(input_path)
    img = img.convert("RGB")  # 确保图像为RGB模式
    width, height = img.size

    # 寻找白色水印区域的高度 N
    N = 0
    for n in range(1, height + 1):
        if any(pixel[:3] != (255, 255, 255) for pixel in img.crop((0, height - n, 1, height - n + 1)).getdata()):
            N = n - 1
            break

    # 分离原图和水印部分
    photo_region = img.crop((0, 0, width, height - N - fix))
    watermark_region = img.crop((0, height - N, width, height))

    # 高斯模糊
    blurred_watermark = img.crop((0, height - 2*N - fix, width, height - N - fix)).filter(ImageFilter.GaussianBlur(100.0))

    # 反转水印
    inverted_region = ImageOps.invert(watermark_region.convert("RGB")).convert("RGBA")

    # 白色
    white_layer = Image.new("RGBA", inverted_region.size, (255, 255, 255, 255))
    # white_layer.putalpha(128)

    # 转换为灰度图像
    alpha_channel = inverted_region.convert("L")
    alpha_channel = ImageEnhance.Brightness(alpha_channel).enhance(alpha_text)
    white_layer.putalpha(alpha_channel)  # 设置为 white_layer 的 alpha 通道

    blurred_watermark = blurred_watermark.convert("RGBA")
    white_layer = white_layer.convert("RGBA")
    
    # 合并
    combined = Image.alpha_composite(blurred_watermark, white_layer)

    # ===== Red Leica Start =====

    if leica_var == True:

        watermark_region = watermark_region.convert("RGB")

        # 遍历找到`最左侧`的像素
        x1, y1 = None, None
        for x in range(watermark_region.width):
            for y in range(watermark_region.height):
                pixel = watermark_region.getpixel((x, y))
                if pixel == leica_color_1 or pixel == leica_color_2 or pixel == leica_color_3:
                    x1, y1 = x, y
                    break
            if x1 is not None:
                break

        # 遍历找到`最右侧`的像素
        x2, y2 = None, None
        for x in range(watermark_region.width - 1, -1, -1):
            for y in range(watermark_region.height):
                pixel = watermark_region.getpixel((x, y))
                if pixel == leica_color_1 or pixel == leica_color_2 or pixel == leica_color_3:
                    x2, y2 = x, y
                    break
            if x2 is not None:
                break

        # 遍历找到`最上方`的像素
        x3, y3 = None, None
        for y in range(watermark_region.height):
            for x in range(watermark_region.width):
                pixel = watermark_region.getpixel((x, y))
                if pixel == leica_color_1 or pixel == leica_color_2 or pixel == leica_color_3:
                    x3, y3 = x, y
                    break
            if x3 is not None:
                break

        # 遍历找到`最下方`的像素
        x4, y4 = None, None
        for y in range(watermark_region.height - 1, -1, -1):
            for x in range(watermark_region.width):
                pixel = watermark_region.getpixel((x, y))
                if pixel == leica_color_1 or pixel == leica_color_2 or pixel == leica_color_3:
                    x4, y4 = x, y
                    break
            if x4 is not None:
                break

        # 没有找到目标颜色，输出错误信息
        if x1 is None:
            print(f"文件{filename}：未能定位到徕卡Logo，请导入包含水印的原图。跳过此文件。")
            continue

        # 输出调试信息
        # print(f"徕卡Logo定位左侧像素位置: ({x1}, {y1})")
        # print(f"徕卡Logo定位右侧像素位置: ({x2}, {y2})")
        # print(f"徕卡Logo定位上方像素位置: ({x3}, {y3})")
        # print(f"徕卡Logo定位下方像素位置: ({x4}, {y4})")

        # 缩放 logo，使其宽度与 x1 和 x2 之间的距离相匹配
        logo_width = x2 - x1 + fix2 * 2
        logo_height = logo_width
        logo_resized = logo.resize((logo_width, logo_height))

        # 计算 logo 放置的左上角位置
        logo_x = x1 - fix2
        logo_y = y3 - fix2

        # 将 logo 粘贴到水印区域
        combined.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # ===== Red Leica END =====

    # 创建并保存图像
    output_img = Image.new("RGB", (width, height - fix))
    output_img.paste(photo_region, (0, 0))
    output_img.paste(combined, (0, height - N - fix))

    output_path = os.path.join(output_dir, filename)
    output_img.save(output_path, quality=100)

    print(f"文件{filename}：转换完成。")

print("图像处理完成！")
