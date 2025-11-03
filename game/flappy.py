import pygame
import random
import sys
import serial
import time
import platform
import asyncio

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (100, 200, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class ButtonReader:
    def __init__(self, port='COM9', baud_rate=9600):
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=1.0
            )
            time.sleep(2)  # Allow Arduino to reset
            self.connected = True
            print(f"Connected to Arduino on {port}")
        except:
            self.connected = False
            print(f"Failed to connect to Arduino on {port}")

    def parse_button_line(self, line: str) -> tuple[int, int]:
        """Parse button states from Arduino serial line"""
        button1 = 0
        button2 = 0
        try:
            if "Button 1:" in line:
                value = line.split(":")[1].strip()
                button1 = int(float(value))
            elif "Button 2:" in line:
                value = line.split(":")[1].strip()
                button2 = int(float(value))
        except (ValueError, IndexError) as e:
            print(f"Error parsing line '{line}': {e}")
        return button1, button2

    def read_sensors(self) -> tuple[bool, bool]:
        """Read current button states from Arduino and detect presses"""
        if not self.connected:
            return False, False

        button1 = 0
        button2 = 0
        static_prev_button1 = 0
        static_prev_button2 = 0

        try:
            if self.serial_port.in_waiting:
                line = self.serial_port.readline()
                if line:
                    try:
                        line = line.decode('utf-8').strip()
                        button1, button2 = self.parse_button_line(line)
                    except UnicodeDecodeError:
                        print(f"Error decoding line: {line}")
        except:
            pass

        # Detect button press (transition from 0 to 1)
        button1_pressed = button1 == 1 and static_prev_button1 == 0
        button2_pressed = button2 == 1 and static_prev_button2 == 0

        # Update previous states for next call
        static_prev_button1 = button1
        static_prev_button2 = button2

        return button1_pressed, button2_pressed

    def close(self):
        """Close serial connection"""
        if self.connected:
            self.serial_port.close()

class Bird:
    def __init__(self, x, color, name):
        self.x = x
        self.y = SCREEN_HEIGHT // 2
        self.radius = 35
        self.velocity = 0
        self.gravity = 1.2
        self.jump_strength = -18
        self.color = color
        self.name = name
        self.alive = True
        
    def update(self):
        if not self.alive:
            return
            
        self.velocity += self.gravity
        self.y += self.velocity
        
        # Check bounds
        if self.y + self.radius >= SCREEN_HEIGHT or self.y - self.radius <= 0:
            self.alive = False
        
    def jump(self):
        if self.alive:
            self.velocity = self.jump_strength
        
    def draw(self, screen):
        if not self.alive:
            # Draw dead bird (gray)
            pygame.draw.circle(screen, (128, 128, 128), (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
            return
            
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        # Draw eye
        pygame.draw.circle(screen, BLACK, (int(self.x + 14), int(self.y - 8)), 5)
        # Draw beak
        pygame.draw.polygon(screen, RED, [(int(self.x + 25), int(self.y)), 
                                        (int(self.x + 40), int(self.y - 8)), 
                                        (int(self.x + 40), int(self.y + 8))])
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 120
        self.gap = 320
        self.top_height = random.randint(80, SCREEN_HEIGHT - self.gap - 80)
        self.bottom_height = SCREEN_HEIGHT - self.top_height - self.gap
        self.speed = 5
        self.passed_player1 = False
        self.passed_player2 = False
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(screen, DARK_GREEN, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, BLACK, (self.x, 0, self.width, self.top_height), 2)
        
        # Draw bottom pipe
        bottom_y = self.top_height + self.gap
        pygame.draw.rect(screen, DARK_GREEN, (self.x, bottom_y, self.width, self.bottom_height))
        pygame.draw.rect(screen, BLACK, (self.x, bottom_y, self.width, self.bottom_height), 2)
        
        # Draw pipe caps
        cap_height = 50
        cap_width = self.width + 20
        cap_x = self.x - 10
        
        # Top cap
        pygame.draw.rect(screen, GREEN, (cap_x, self.top_height - cap_height, cap_width, cap_height))
        pygame.draw.rect(screen, BLACK, (cap_x, self.top_height - cap_height, cap_width, cap_height), 2)
        
        # Bottom cap
        pygame.draw.rect(screen, GREEN, (cap_x, bottom_y, cap_width, cap_height))
        pygame.draw.rect(screen, BLACK, (cap_x, bottom_y, cap_width, cap_height), 2)
        
    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.top_height + self.gap, self.width, self.bottom_height)
        return top_rect, bottom_rect
        
    def is_offscreen(self):
        return self.x + self.width < 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Two Player Championship")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 72)
        self.big_font = pygame.font.Font(None, 144)
        self.small_font = pygame.font.Font(None, 48)
        
        # Initialize Arduino button reader
        self.button_reader = ButtonReader()
        
        self.reset_game()
        
    def reset_game(self):
        self.player1 = Bird(300, YELLOW, "Player 1")
        self.player2 = Bird(400, ORANGE, "Player 2")
        self.pipes = []
        self.score1 = 0
        self.score2 = 0
        self.game_over = False
        self.game_started = False
        self.winner = None
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                # Keyboard controls for testing
                if event.key == pygame.K_w:  # Player 1 alternative
                    if not self.game_started:
                        self.game_started = True
                    elif self.game_over:
                        self.reset_game()
                    else:
                        self.player1.jump()
                elif event.key == pygame.K_UP:  # Player 2 alternative
                    if not self.game_started:
                        self.game_started = True
                    elif self.game_over:
                        self.reset_game()
                    else:
                        self.player2.jump()
                elif event.key == pygame.K_SPACE:  # Start/restart
                    if not self.game_started:
                        self.game_started = True
                    elif self.game_over:
                        self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        # Read Arduino buttons
        button1_pressed, button2_pressed = self.button_reader.read_sensors()
        
        if button1_pressed:
            if not self.game_started:
                self.game_started = True
            elif self.game_over:
                self.reset_game()
            else:
                self.player1.jump()
                
        if button2_pressed:
            if not self.game_started:
                self.game_started = True
            elif self.game_over:
                self.reset_game()
            else:
                self.player2.jump()
                
        return True
        
    def update(self):
        if not self.game_started or self.game_over:
            return
            
        self.player1.update()
        self.player2.update()
        
        # Check if both players are dead
        if not self.player1.alive and not self.player2.alive:
            self.game_over = True
            if self.score1 > self.score2:
                self.winner = "Player 1"
            elif self.score2 > self.score1:
                self.winner = "Player 2"
            else:
                self.winner = "Tie"
            
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.is_offscreen():
                self.pipes.remove(pipe)
                
        # Add new pipes $

        if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - 500:
            self.pipes.append(Pipe(SCREEN_WIDTH))
        # Check collisions and scoring
        player1_rect = self.player1.get_rect()
        player2_rect = self.player2.get_rect()
        
        for pipe in self.pipes:
            top_rect, bottom_rect = pipe.get_rects()
            
            # Check Player 1 collision
            if self.player1.alive and (player1_rect.colliderect(top_rect) or player1_rect.colliderect(bottom_rect)):
                self.player1.alive = False
                
            # Check Player 2 collision
            if self.player2.alive and (player2_rect.colliderect(top_rect) or player2_rect.colliderect(bottom_rect)):
                self.player2.alive = False
                
            # Check if players passed pipe
            if not pipe.passed_player1 and self.player1.alive and self.player1.x > pipe.x + pipe.width:
                pipe.passed_player1 = True
                self.score1 += 1
                
            if not pipe.passed_player2 and self.player2.alive and self.player2.x > pipe.x + pipe.width:
                pipe.passed_player2 = True
                self.score2 += 1
    def draw(self):
        # Draw background
        self.screen.fill(BLUE)
        
        # Draw center line
        pygame.draw.line(self.screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        
        # Draw clouds
        for i in range(8):
            x = 200 + i * 250
            y = 120 + (i % 2) * 60
            pygame.draw.circle(self.screen, WHITE, (x, y), 40)
            pygame.draw.circle(self.screen, WHITE, (x + 30, y), 30)
            pygame.draw.circle(self.screen, WHITE, (x + 60, y), 40)
            
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
            
        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # Draw scores and player info
        score1_text = self.font.render(f"Player 1: {self.score1}", True, YELLOW)
        score2_text = self.font.render(f"Player 2: {self.score2}", True, ORANGE)
        self.screen.blit(score1_text, (20, 20))
        self.screen.blit(score2_text, (20, 100))
        
        # Draw connection status
        if self.button_reader.connected:
            status_text = self.small_font.render("Arduino Connected", True, GREEN)
        else:
            status_text = self.small_font.render("Arduino Disconnected - Use W/UP keys", True, RED)
        self.screen.blit(status_text, (20, SCREEN_HEIGHT - 60))
        
        # Draw game states
        if not self.game_started:
            title_text = self.big_font.render("Flappy Bird Championship", True, BLACK)
            player1_text = self.font.render("Player 1 (Yellow) - Button 1 or W", True, YELLOW)
            player2_text = self.font.render("Player 2 (Orange) - Button 2 or UP", True, ORANGE)
            start_text = self.font.render("Press any button to start!", True, BLACK)
            
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 300))
            self.screen.blit(player1_text, (SCREEN_WIDTH // 2 - player1_text.get_width() // 2, 500))
            self.screen.blit(player2_text, (SCREEN_WIDTH // 2 - player2_text.get_width() // 2, 580))
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 700))
            
        elif self.game_over:
            game_over_text = self.big_font.render("Game Over!", True, RED)
            winner_text = self.font.render(f"Winner: {self.winner}", True, BLACK)
            final_score_text = self.font.render(f"Final Scores - P1: {self.score1}, P2: {self.score2}", True, BLACK)
            restart_text = self.font.render("Press any button to restart", True, BLACK)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 400))
            self.screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, 560))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 640))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 720))
            
        # Draw player status
        if self.game_started and not self.game_over:
            if not self.player1.alive:
                dead_text = self.font.render("DEAD", True, RED)
                self.screen.blit(dead_text, (self.player1.x - 50, self.player1.y - 100))
            if not self.player2.alive:
                dead_text = self.font.render("DEAD", True, RED)
                self.screen.blit(dead_text, (self.player2.x - 50, self.player2.y - 100))
            
        pygame.display.flip()

async def main():
    game = Game()
    while True:
        game.handle_events()
        game.update()
        game.draw()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())