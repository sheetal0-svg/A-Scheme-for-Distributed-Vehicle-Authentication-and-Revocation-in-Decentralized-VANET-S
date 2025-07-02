import pygame
import sys
import random
import csv
import datetime

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
        surface.blit(text, (int(self.x)+5, self.y+5))

# Simple Button class
class Button:
    def __init__(self, rect, color, text):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.text = text
        self.text_surface = font.render(text, True, BLACK)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        surface.blit(self.text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Simulate blockchain txid
def simulate_blockchain_anchor(data):
    return ''.join(random.choices('0123456789abcdef', k=16))

# Draw road
def draw_road(surface):
    pygame.draw.rect(surface, GRAY, (0, ROAD_Y1, WIDTH, ROAD_Y2-ROAD_Y1))
    # lane dashed lines
    dash_length = 20
    gap = 20
    x = 0
    while x < WIDTH:
        pygame.draw.line(surface, YELLOW, (x, LANE_Y), (x+dash_length, LANE_Y), 4)
        x += dash_length + gap

# Draw RSUs
def draw_rsus(surface):
    for pos in RSUS:
        pygame.draw.rect(surface, BLUE, (*pos, 40, 40))
        label = font.render("RSU", True, BLACK)
        surface.blit(label, (pos[0]+7, pos[1]+12))

# Show instructions
def draw_instructions(surface):
    lines = [
        "Press keyboard A/R/E/Q or click buttons below to simulate events",
    ]
    for i, line in enumerate(lines):
        text = font.render(line, True, BLACK)
        surface.blit(text, (10, 10 + i*22))

def export_logs(log):
    if not log:
        print("No logs to export.")
        return

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

    # Define buttons
    buttons = {
        "auth": Button((50, 420, 150, 50), (100, 200, 100), "Authenticate Car1"),
        "revoke": Button((250, 420, 150, 50), (200, 100, 100), "Revoke Car2"),
        "export": Button((450, 420, 150, 50), (100, 100, 200), "Export Logs"),
        "quit": Button((650, 420, 150, 50), (150, 150, 150), "Quit"),
    }

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

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if buttons["auth"].is_clicked(pos):
                    txid = simulate_blockchain_anchor("Auth-Car1")
                    log_entry = {
                        "time": now,
                        "event": "Authentication",
                        "vehicle": "Car1",
                        "details": "Vehicle authenticated via RSU 1",
                        "blockchain_tx": txid
                    }
                    logs.append(log_entry)
                    print(f"Authentication clicked: TxID={txid}")

                elif buttons["revoke"].is_clicked(pos):
                    txid = simulate_blockchain_anchor("Revoke-Car2")
                    log_entry = {
                        "time": now,
                        "event": "Revocation",
                        "vehicle": "Car2",
                        "details": "Vehicle revoked due to misbehavior at RSU 2",
                        "blockchain_tx": txid
                    }
                    logs.append(log_entry)
                    print(f"Revocation clicked: TxID={txid}")

                elif buttons["export"].is_clicked(pos):
                    export_logs(logs)

                elif buttons["quit"].is_clicked(pos):
                    running = False

        for car in cars:
            car.move()
            car.draw(screen)

        # Display the latest status message on screen (above buttons)
        status_y = 380
        status_bg_rect = pygame.Rect(0, status_y, WIDTH, 30)
        pygame.draw.rect(screen, WHITE, status_bg_rect)  # clear area

        if logs:
            last_log = logs[-1]
            status_text = f"{last_log['event']} for {last_log['vehicle']}: TxID={last_log['blockchain_tx']}"
            status_surface = font.render(status_text, True, BLACK)
            screen.blit(status_surface, (10, status_y + 5))
        else:
            status_surface = font.render("No events yet.", True, BLACK)
            screen.blit(status_surface, (10, status_y + 5))

        # Draw buttons on top
        for btn in buttons.values():
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
