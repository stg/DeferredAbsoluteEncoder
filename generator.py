from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QPushButton, QFileDialog
from PyQt5.QtCore import QRect
from array import array
import math
import sys

class SvgViewer(QWidget):
    def save_svg(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","SVG Files (*.svg);;All Files (*.*)", options=options)
        if fileName:
            f = open(fileName, "wb")
            f.write(self.svg)
            f.close()            

    def save_lut(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","C Files (*.c);;All Files (*.*)", options=options)
        if fileName:
            f = open(fileName, "wb")
            f.write(self.lut)
            f.close()
    
    def __init__(self, w, h, svg, lut):
        super().__init__()
        
        qtRectangle = QRect(0, 0, w, h + 50)
        qtRectangle.moveCenter(QDesktopWidget().availableGeometry().center())
        self.setGeometry(qtRectangle)
        
        self.svg = svg
        self.lut = lut
        
        widgetSvg = QSvgWidget(parent = self)
        widgetSvg.setGeometry(0, 0, w, h)
        widgetSvg.load(svg)
        
        button = QPushButton("&Save SVG", parent = self)
        button.setGeometry(int(w / 2 - 175), int(h + 10), 150, 30)
        button.clicked.connect(self.save_svg)

        button = QPushButton("&Save LUT", parent = self)
        button.setGeometry(int(w / 2 + 25), int(h + 10), 150, 30)
        button.clicked.connect(self.save_lut)

def find_period(initial, polynomial):
    period = 1
    depth = 1
    lfsr = initial
    while True:
        lfsr = (lfsr >> 1) ^ (-(lfsr & 1) & polynomial)
        period = period + 1
        if lfsr == initial: break
    while period > (1 << depth):
        depth = depth + 1
    return (depth, period)

if __name__ == "__main__":

    # Known maximum-length polynomials LENGTH: POLYNOMIAL-LIST
    #   16: 9 C
    #   32: 12 14 17 1B 1D 1E
    #   64: 21 2D 30 33 36 39
    #  128: 41 44 47 48 4E 53 55 5C 5F 60 65 69 6A 72 77 78 7B 7E
    #  256: 8E 95 96 A6 AF B1 B2 B4 B8 C3 C6 D4 E1 E7 F3 FA
    #  512: 108 10D 110 116 119 12C 12F 134 137 13B 13E 143 14A 151 152 157 15B 15E 167 168 16D 17A 17C 189 
    #       18A 18F 191 198 19D 1A7 1AD 1B0 1B5 1B6 1B9 1BF 1C2 1C7 1DA 1DC 1E3 1E5 1E6 1EA 1EC 1F1 1F4 1FD
    # 1024: 204 20D 213 216 232 237 240 245 262 26B 273 279 27F 286 28C 291 298 29E 2A1 2AB 2B5 2C2 2C7 2CB 2D0 2E3 2F2 2FB 2FD 309
    #       30A 312 31B 321 327 32D 33C 33F 344 35A 360 369 36F 37E 38B 38E 390 39C 3A3 3A6 3AA 3AC 3B1 3BE 3C6 3C9 3D8 3ED 3F9 3FC
    
    polynomial = 0xB8 # Polynomial

    # Find period
    print('Finding period...')
    (depth, period) = find_period(1, polynomial)
    print(f'\tPeriod for polynomial 0x{polynomial:01X} is {period}')

    # Generate bitstream
    print('Generating bitstream...')
    print('\t0', end = '')
    bits = array('B', [0] * (period + 1))
    lfsr = 1    # initial state
    for i in range(1, period):
        rlsb = lfsr & 1
        lfsr = lfsr >> 1
        if rlsb:
            lfsr = lfsr ^ polynomial
        bits[i] = rlsb
        print(rlsb, end = '\n' if i == period - 1 else '' if 63 != i & 63 else '\n\t')
        
    # Check for collisions just in case - an LFSR really shouldn't have any
    print('Checking bitstream...')
    if(period <= 1024):
        for i in range(period):
            for j in range(period - 1):
                for k in range(depth + 1):
                    if bits[(i + k) % period] != bits[(i + j + k + 1) % period]:
                        break
                if k == depth: break
            if k == depth: break
        if k == depth:
            print(f'\tCollision found: {i} = {j}')
        else:
            print('\tNo collisions')
    else:
        # Would be too slow...
        print('\tSkipping (too slow)')

    # Radius of wheel
    wheel_radius = 250

    # Radii for quadrature encoder ring
    # Set to 0 to remove this ring
    quad_inner_radius  = 190
    quad_outer_radius  = 210

    # Radii for bitstream encoder ring
    bits_fraction      = 1.0
    bits_inner_radius  = 220
    bits_outer_radius  = 240

    # Generate resources
    print('Generating resources...')

    balance_x = 0
    balance_y = 0

    # Generate SVG
    svg = f'<svg viewBox="{-(wheel_radius) * 1.05} {-(wheel_radius) * 1.05} {(wheel_radius) * 2.1} {(wheel_radius) * 2.1}" xmlns="http://www.w3.org/2000/svg">\n'.encode('utf-8')
    svg = svg + f'\t<circle cx="0" cy="0" r="{(wheel_radius)}" stroke="black" fill="white" stroke-width="1" />\n'.encode('utf-8')
    for i in range(period):
        if bits[i]:
            v0 = ((math.pi * 2) / period) * (i + (0 + ((1 - bits_fraction) / 2)));
            v1 = ((math.pi * 2) / period) * (i + (1 - ((1 - bits_fraction) / 2)));
            balance_x = balance_x + math.sin((v0 + v1) / 2)
            balance_y = balance_y + math.cos((v0 + v1) / 2)
            svg = svg + (   
                f'\t<polygon points="'
                f'{math.sin(v0) * bits_inner_radius},{math.cos(v0) * bits_inner_radius} '
                f'{math.sin(v0) * bits_outer_radius},{math.cos(v0) * bits_outer_radius} '
                f'{math.sin(v1) * bits_outer_radius},{math.cos(v1) * bits_outer_radius} '
                f'{math.sin(v1) * bits_inner_radius},{math.cos(v1) * bits_inner_radius}'
                f'" style="fill:black;" />\n'
            ).encode('utf-8')

    balance_x /= period
    balance_y /= period
    # Center
    svg = svg + f'\t<circle cx="0" cy="0" r="{(wheel_radius / 50)}" stroke="black" fill="green" stroke-width="1" />\n'.encode('utf-8')
    # Center of mass
    #svg = svg + f'\t<circle cx="{balance_x * wheel_radius}" cy="{balance_y * wheel_radius}" r="{(wheel_radius / 50)}" stroke="black" fill="red" stroke-width="1" />\n'.encode('utf-8')

    if quad_inner_radius and quad_outer_radius:
        for i in range(period // 2):
            if i & 1:
                v0 = ((math.pi * 4) / period) * (i + 0.25);
                v1 = ((math.pi * 4) / period) * (i + 1.25);
                svg = svg + (
                    f'\t<polygon points="'
                    f'{math.sin(v0) * quad_inner_radius},{math.cos(v0) * quad_inner_radius} '
                    f'{math.sin(v0) * quad_outer_radius},{math.cos(v0) * quad_outer_radius} '
                    f'{math.sin(v1) * quad_outer_radius},{math.cos(v1) * quad_outer_radius} '
                    f'{math.sin(v1) * quad_inner_radius},{math.cos(v1) * quad_inner_radius}'
                    f'" style="fill:black;" />\n'
                ).encode('utf-8')


    svg = svg + f'</svg>'.encode('utf-8')

    # Generate LUT
    luta = array('L', [0] * period)
    for i in range(period):
        j = 0
        for k in range(depth):
            j = (j << 1) | bits[(i + k) % period]
        luta[j] = i
    bit_size = 32 if depth > 16 else 16 if depth > 8 else 8
    hex_size = (depth + 3) // 4
    lut = f'const uint{bit_size}_t quadrature_lut[] = {{\n\t'.encode('utf-8')
    for i in range(period):
        lut = lut + f'0x{luta[i]:0{hex_size}X}'.encode('utf-8')
        if i == period - 1:
            lut = lut + '\n'.encode('utf-8')
        else:
            if 15 == i & 15:
                lut = lut + ',\n\t'.encode('utf-8')
            else:
                lut = lut + ', '.encode('utf-8')
    lut = lut + '};\n'.encode('utf-8')

    print('\tDone')
    
    # Launch the UI
    app = QApplication([])
    window = SvgViewer(1000, 1000, svg, lut)
    window.show()
    app.exec()
