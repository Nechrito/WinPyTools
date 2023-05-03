import os
import sys
from PIL import Image
import string


class PixelArtAnalyzer:
    def __init__(self, file_path, pixel_size=None):
        self.file_path = file_path
        self.image = Image.open(file_path).convert("RGBA")
        self.width, self.height = self.image.size
        self.pixel_size = pixel_size or self.get_pixel_size()
        self.sprite_size = (self.width, self.height)
        self.frame_grid = self.map_frames()
        self.unique_rgba_values = self.get_unique_rgba_values()
        self.rgba_char_map = self.create_rgba_char_map()

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
        resized_image = image_no_alpha.resize(
            (new_width, new_height), Image.NEAREST)
        return resized_image

    def remove_transparency(self):
        if self.image.mode == 'RGBA':
            bg = Image.new('RGBA', self.image.size, (255, 255, 255, 255))
            bg.paste(self.image, (0, 0), self.image)
            return bg.convert('RGB')
        else:
            return self.image

    def get_unique_rgba_values(self):
        unique_rgba_values = set()
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.image.getpixel((x, y))
                unique_rgba_values.add(pixel)
        return unique_rgba_values

    def create_rgba_char_map(self):
        chars = string.ascii_letters + string.digits + string.punctuation + " "
        rgba_char_map = {}
        for i, rgba_value in enumerate(self.unique_rgba_values):
            rgba_char_map[rgba_value] = chars[i %
                                              len(chars)]  # .replace("p", " ")

        return rgba_char_map

    def print_ascii_art(self):
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.image.getpixel((x, y))
                if pixel in self.rgba_char_map:
                    print(self.rgba_char_map[pixel], end="")
                else:
                    print(" ", end="")
            print()

    def print_info(self):
        print(f"File path: {self.file_path}")
        print(f"Image size: {self.width}x{self.height}")
        print(f"Pixel size: {self.pixel_size}")
        print(f"Sprite size: {self.sprite_size[0]}x{self.sprite_size[1]}")

    # def generate_uv_map(self):
    #     print("\nGenerating UV map...\n")
    #     uv_map = []
    #     for y in range(self.height):
    #         row = []
    #         for x in range(self.width):
    #             pixel = self.image.getpixel((x, y))
    #             if pixel in self.rgba_char_map:
    #                 char = self.rgba_char_map[pixel]
    #                 u = ord(char) / len(self.rgba_char_map)
    #                 v = y / self.height
    #                 row.append((round(u, 2), round(v, 2)))
    #             else:
    #                 row.append(None)
    #         uv_map.append(row)
    #     return uv_map

    def generate_uv_map(self):
        uv_map_image = Image.new(
            'RGBA', (self.width, self.height), (0, 0, 0, 0))
        uv_map = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        used_colors = list(self.unique_rgba_values)
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.image.getpixel((x, y))
                color_index = used_colors.index(pixel)
                uv_x, uv_y = x % len(used_colors), color_index
                uv_map_image.putpixel((uv_x, uv_y), pixel)
                uv_map[uv_y][uv_x] = self.rgba_char_map[pixel]

        uv_map_image.save("uv_map.png", "PNG")
        return uv_map


def write_output(uv_map, frame_grid, output):
    file_path = sys.argv[1]

    # Write to text file with the same name as the file extracted from the path (without the extension)
    file_name = file_path.split("\\")[-1].split(".")[0]

    # Create a directory called "sprites" if it doesn't exist
    if not os.path.exists("sprites"):
        os.mkdir("sprites")

    # Write the UV map to a text file in the "sprites" directory
    uv_map_path = os.path.join("sprites", f"{file_name}_uv_map.txt")
    with open(uv_map_path, "w") as f:
        for row in uv_map:
            f.write(''.join(row) + "\n")

    # Write the text file to the "sprites" directory
    path = os.path.join("sprites", f"{file_name}.txt")
    with open(path, "w") as f:
        f.write(str(frame_grid))


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python pixel_art_analyzer.py <image_file_path> [pixel_size]")
        sys.exit(1)

    file_path = sys.argv[1]
    pixel_size = 1
    if len(sys.argv) > 2:
        print("Pixel size set to:", sys.argv[2])
        pixel_size = int(sys.argv[2])

    analyzer = PixelArtAnalyzer(file_path, pixel_size)
    analyzer.print_info()
    analyzer.print_ascii_art()
    uv_map = analyzer.generate_uv_map()
    output = print(repr(analyzer))
    print("\nDone!")

    write_output(uv_map, analyzer.frame_grid, output)


if __name__ == "__main__":
    main()
