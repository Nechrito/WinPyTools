import sys
from PIL import Image

class PixelArtAnalyzer:
    def __init__(self, file_path, pixel_size=None):
        self.file_path = file_path
        self.image = Image.open(file_path).convert("RGBA")
        self.width, self.height = self.image.size
        self.pixel_size = pixel_size or self.get_pixel_size()
        self.sprite_size = (self.width, self.height)  # Set the sprite_size to the full image size
        self.frame_grid = self.map_frames()

    def get_pixel_size(self):
        half_width = self.width // 2
        half_height = self.height // 2

        size = 1
        last_pixel = self.image.getpixel((half_width, 0))

        for y in range(1, self.height):
            pixel = self.image.getpixel((half_width, y))
            if pixel != last_pixel:
                break
            size += 1

        return size if size != self.height else 1

    def get_sprite_size(self):
        return self.width // self.pixel_size, self.height // self.pixel_size

    def map_frames(self):
        frame_grid = []
        for y in range(0, self.height, self.sprite_size[1]):
            row = []
            for x in range(0, self.width, self.sprite_size[0]):
                frame = []
                for inner_y in range(y, y + self.sprite_size[1]):
                    frame_row = []
                    for inner_x in range(x, x + self.sprite_size[0]):
                        pixel = self.image.getpixel((inner_x, inner_y))
                        frame_row.append(pixel)
                    frame.append(frame_row)
                row.append(frame)
            frame_grid.append(row)

        return frame_grid

    def resize_image(self):
        image_no_alpha = self.remove_transparency()
        new_width = self.width // self.pixel_size
        new_height = self.height // self.pixel_size
        resized_image = image_no_alpha.resize((new_width, new_height), Image.NEAREST)
        return resized_image

    def remove_transparency(self):
        if self.image.mode == 'RGBA':
            bg = Image.new('RGBA', self.image.size, (255, 255, 255, 255))
            bg.paste(self.image, (0, 0), self.image)
            return bg.convert('RGB')
        else:
            return self.image

    def print_ascii_art(self):
        resized_image = self.resize_image()
        width, height = resized_image.size

        ascii_symbols = "         #" # " .:-=+*%@#"
        num_symbols = len(ascii_symbols)

        for y in range(height):
            for x in range(width):
                pixel = resized_image.getpixel((x, y))
                if len(pixel) == 3:
                    r, g, b = pixel
                    a = 255
                else:
                    r, g, b, a = pixel
                if a == 0:
                    print(" ", end="")
                else:
                    brightness = (r + g + b) / 3
                    index = int(brightness * num_symbols / 256)
                    print(ascii_symbols[index], end="")
            print()




    def print_info(self):
        print(f"File path: {self.file_path}")
        print(f"Image size: {self.width}x{self.height}")
        print(f"Pixel size: {self.pixel_size}")
        print(f"Sprite size: {self.sprite_size[0]}x{self.sprite_size[1]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pixel_art_analyzer.py <image_file_path> [pixel_size]")
        sys.exit(1)

    file_path = sys.argv[1]
    pixel_size = int(sys.argv[2]) if len(sys.argv) > 2 else None
    analyzer = PixelArtAnalyzer(file_path, pixel_size)

    analyzer.print_info()
    analyzer.print_ascii_art()
