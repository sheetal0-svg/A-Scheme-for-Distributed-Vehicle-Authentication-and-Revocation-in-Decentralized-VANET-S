import time
from tkinter import *
from tkinter.filedialog import askopenfilename

from PIL import ImageTk, Image
import sqlite3
import os
import pygame
import sys
import random
import csv
import datetime
root = Tk()
root.geometry('1366x768')
root.title("Vanet")
canv = Canvas(root, width=1366, height=768, bg='white')
canv.grid(row=2, column=3)
img = Image.open('back.png')
photo = ImageTk.PhotoImage(img)
canv.create_image(1, 1, anchor=NW, image=photo)
File = StringVar()


def veh1():
    os.system("python vehreg1.py")


def veh2():
    os.system('python simulation.py')

def veh3():
    os.system('python blockchain.py')
    pygame.init()
    WIDTH, HEIGHT = 900, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("VANET Authentication & Revocation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 18)

    # Colors
    GRAY = (105, 105, 105)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    RED = (220, 20, 60)
    GREEN = (0, 180, 0)
    ORANGE = (255, 140, 0)
    LIGHTGRAY = (211, 211, 211)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Road and lane positions
    ROAD_Y1, ROAD_Y2 = 200, 300
    LANE_Y = (ROAD_Y1 + ROAD_Y2) // 2

    # RSU positions
    RSUS = [(100, 170), (450, 170), (800, 170)]

    # Car class
    class Car:
        def __init__(self, x, y, color, name):
            self.x = x
            self.y = y
            self.color = color
            self.name = name
            self.speed = random.uniform(1.0, 2.5)

        def move(self):
            self.x += self.speed
            if self.x > WIDTH:
                self.x = -70  # reset to left off-screen

        def draw(self, surface):
            pygame.draw.rect(surface, self.color, (int(self.x), self.y, 60, 30))
            text = font.render(self.name, True, WHITE)
            surface.blit(text, (int(self.x) + 5, self.y + 5))

    # Simulate blockchain txid
    def simulate_blockchain_anchor(data):
        return ''.join(random.choices('0123456789abcdef', k=16))

    # Draw road
    def draw_road(surface):
        pygame.draw.rect(surface, GRAY, (0, ROAD_Y1, WIDTH, ROAD_Y2 - ROAD_Y1))
        # lane dashed lines
        dash_length = 20
        gap = 20
        x = 0
        while x < WIDTH:
            pygame.draw.line(surface, YELLOW, (x, LANE_Y), (x + dash_length, LANE_Y), 4)
            x += dash_length + gap

    # Draw RSUs
    def draw_rsus(surface):
        for pos in RSUS:
            pygame.draw.rect(surface, BLUE, (*pos, 40, 40))
            label = font.render("RSU", True, BLACK)
            surface.blit(label, (pos[0] + 7, pos[1] + 12))

    # Show instructions
    def draw_instructions(surface):
        lines = [
            "Press A: Simulate Authentication (Car1)",
            "Press R: Simulate Revocation (Car2)",
            "Press E: Export Logs to CSV",
            "Press Q or ESC: Quit"
        ]
        for i, line in enumerate(lines):
            text = font.render(line, True, BLACK)
            surface.blit(text, (10, 10 + i * 22))

    def export_logs(log):
        if not log:
            print("No logs to export.")
            return

        # Use file dialog alternative - simple fixed filename for demo
        filename = "vanet_logs.csv"
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['time', 'event', 'vehicle', 'details', 'blockchain_tx']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for entry in log:
                    writer.writerow(entry)
            print(f"Logs exported successfully to {filename}")
        except Exception as e:
            print("Failed to export logs:", e)

    def main():
        cars = [
            Car(150, 230, RED, "Car1"),
            Car(400, 230, GREEN, "Car2"),
            Car(650, 230, ORANGE, "Car3"),
        ]
        logs = []

        running = True
        while running:
            screen.fill(LIGHTGRAY)
            draw_road(screen)
            draw_rsus(screen)
            draw_instructions(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_a:
                        # Auth simulation for Car1
                        txid = simulate_blockchain_anchor("Auth-Car1")
                        log_entry = {
                            "time": now,
                            "event": "Authentication",
                            "vehicle": "Car1",
                            "details": "Vehicle authenticated via RSU 1",
                            "blockchain_tx": txid
                        }
                        logs.append(log_entry)
                        print(f"Authentication simulated: TxID={txid}")
                    elif event.key == pygame.K_r:
                        # Revocation simulation for Car2
                        txid = simulate_blockchain_anchor("Revoke-Car2")
                        log_entry = {
                            "time": now,
                            "event": "Revocation",
                            "vehicle": "Car2",
                            "details": "Vehicle revoked due to misbehavior at RSU 2",
                            "blockchain_tx": txid
                        }
                        logs.append(log_entry)
                        print(f"Revocation simulated: TxID={txid}")
                    elif event.key == pygame.K_e:
                        export_logs(logs)

            for car in cars:
                car.move()
                car.draw(screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    if __name__ == "__main__":
        main()


Button(root, text='Vehicle1 Registration', width=30,height=2, bg='yellow', fg='black', font=("bold", 12), command=veh1).place(x=100,
                                                                                                            y=450)

Button(root, text='Simulation', width=30,height=2, bg='yellow', fg='black', font=("bold", 12), command=veh2).place(
    x=100, y=500)
Button(root, text='Simulation With Blockchain', width=30,height=2, bg='yellow', fg='black', font=("bold", 12), command=veh3).place(x=100, y=550)
root.mainloop()
