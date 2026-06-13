import io
import json
import math
import os
import random
import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2000's Trivia Challenge")
DATA_FILE = os.path.join(os.path.dirname(__file__), "user_data.json")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 180, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (220, 220, 220)
PURPLE = (201, 185, 255)
LIGHT_BLUE = (173, 216, 230)
NAVY = (15, 22, 52)
GOLD = (240, 190, 60)
LIGHT = (235, 236, 242)

title_font = pygame.font.SysFont("comic sans ms", 36, bold=True)
question_font = pygame.font.SysFont("comic sans ms", 20)
option_font = pygame.font.SysFont("comic sans ms", 24)
feedback_font = pygame.font.SysFont("comic sans ms", 30, bold=True)
small_font = pygame.font.SysFont("comic sans ms", 16)



class AuthManager:
    """Handles everything to do with checking, creating, and storing accounts."""
    def __init__(self, data_filepath):
        self.filepath = data_filepath
        self.user_data = self._load_all_data()

    def _load_all_data(self):
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, ValueError):
            return {}

    def register_user(self, username, password):
        if not username or not password:
            return False, "Enter a username and password to register."
        if username in self.user_data:
            return False, "Username already exists. Choose another name."
        
        self.user_data[username] = {
            "password": password,
            "high_score": 0
        }
        self._save_all_data()
        return True, "Account created! Logging in..."

    def authenticate(self, username, password):
        if not username or not password:
            return False, "Please fill in both fields."
        if username in self.user_data and self.user_data[username]["password"] == password:
            return True, "Loaded your profile."
        return False, "Invalid username or password."

    def save_high_score(self, username, final_score):
        if username == "Guest":
            return
        if username in self.user_data:
            if final_score > self.user_data[username].get("high_score", 0):
                self.user_data[username]["high_score"] = final_score
                self._save_all_data()


class InputBox:
    def __init__(self, rect, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.color = WHITE
        self.text = ""
        self.active = False
        self.placeholder = placeholder

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = GOLD if self.active else WHITE
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            elif event.unicode.isprintable() and len(self.text) < 18:
                self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=8)
        if self.text:
            txt = option_font.render(self.text, True, BLACK)
            surface.blit(txt, (self.rect.x + 10, self.rect.y + 8))
        else:
            txt = option_font.render(self.placeholder, True, GRAY)
            surface.blit(txt, (self.rect.x + 10, self.rect.y + 8))


# Initialize Auth Layer
auth = AuthManager(DATA_FILE)
current_user = "Guest"

# State Control: "login" or "game"
game_state = "login"
auth_message = "Sign in or play as a guest player!"

# Input fields and system buttons
username_box = InputBox((220, 180, 360, 45), "Username")
password_box = InputBox((220, 240, 360, 45), "Password")


questions = [
    {
        "question": "What were the Twin Towers rebuilt as?",
        "options": ["One World Trade Center", "Empire State Building", "Burj Khalifa", "Shanghai Tower"],
        "answer": "One World Trade Center"
    },
    {
        "question": "Michael Jackson is known as the King of what?",
        "options": ["Jazz", "Rock", "Pop", "Blues"],
        "answer": "Pop"
    },
    {
        "question": "Who did Michael Jackson start a band with?",
        "options": ["Brothers", "Parents", "Neighbors", "Cousins"],
        "answer": "Brothers"
    },
    {
        "question": "When did Hurricane Katrina hit New Orleans?",
        "options": ["Aug 22nd", "Aug 3rd", "Aug 23rd", "Aug 29th"],
        "answer": "Aug 29th"
    },
    {
        "question": "How many monthly active users does Facebook have approximately?",
        "options": ["3 Billion", "6 Million", "700 Million", "8 Billion"],
        "answer": "3 Billion"
    },
    {
        "question": "Wikipedia was established in what year?",
        "options": ["2001", "2002", "2003", "2004"],
        "answer": "2001"
    },
    {
        "question": "What year was the first iPhone released?",
        "options": ["2001", "2002", "2004", "2007"],
        "answer": "2007"
    },
    {
        "question": "What show was released in 2000-2010 era?",
        "options": ["Survivor", "All-American Girl", "Mr. Bean", "Beast Games"],
        "answer": "Survivor"
    },
    {
        "question": "What movie was released in 2000?",
        "options": ["Gladiator", "The Matrix", "X-Men", "The Lord of the Rings"],
        "answer": "The Matrix"
    },
    {
        "question": "What is the name of the lost clownfish that a father searches for across the ocean?",
        "options": ["Nemo", "Dory", "Shrek", "The Lord of the Ringsfff"],
        "answer": "Nemo"
    }
]

current_questions = []
question_index = 0
score = 0
selected_option = None
game_over = False

# Prevent immediate mouse-click propagation when switching screens
ignore_mouse = False

feedback = ""
feedback_color = BLACK


class Button:
    def __init__(self, x, y, w, h, text, custom_color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.custom_color = custom_color

    def draw(self, surface, selected=False):
        if self.custom_color:
            color = self.custom_color
        else:
            color = LIGHT_BLUE if selected else GRAY

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)

        txt = option_font.render(self.text, True, BLACK if not self.custom_color or self.custom_color == GOLD else WHITE)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def create_buttons():
    buttons = []
    for i in range(4):
        buttons.append(Button(200, 150 + i * 60, 400, 45, ""))
    return buttons

buttons = create_buttons()
next_button = Button(620, 420, 150, 50, "NEXT")

# Login system controls
login_btn = Button(220, 310, 170, 45, "Sign In", BLUE)
register_btn = Button(410, 310, 170, 45, "Register", GREEN)
guest_btn = Button(220, 370, 360, 45, "Play as Guest", GOLD)

# Home / Tutorial buttons (shown after successful login)
# Positioned higher so they don't overlap login buttons
home_start_btn = Button(220, 200, 170, 45, "Start Quiz", BLUE)
home_tutorial_btn = Button(410, 200, 170, 45, "Tutorial", GREEN)
home_logout_btn = Button(220, 260, 360, 45, "Log Out", GOLD)

# Tutorial screen buttons (different positions)
tutorial_start_btn = Button(220, 360, 170, 45, "Start Quiz", BLUE)
tutorial_back_btn = Button(410, 360, 170, 45, "Back", GREEN)


def build_quiz_questions():
    return [
        {
            "question": q["question"],
            "options": random.sample(q["options"], len(q["options"])),
            "answer": q["answer"]
        }
        for q in random.sample(questions, 3)
    ]


def start_game():
    global current_questions, question_index, score, selected_option, game_over, feedback, feedback_color
    print("DEBUG: start_game() called")
    current_questions = build_quiz_questions()
    question_index = 0
    score = 0
    selected_option = None
    game_over = False
    feedback = ""
    feedback_color = BLACK
    load_question()


def load_question():
    global selected_option
    selected_option = None
    q = current_questions[question_index]
    for i in range(4):
        buttons[i].text = q["options"][i]


def check_answer():
    global feedback, feedback_color, score
    correct = current_questions[question_index]["answer"]

    if selected_option == correct:
        score += 1
        feedback = "✅ CORRECT!"
        feedback_color = GREEN
    else:
        feedback = "❌ WRONG!"
        feedback_color = RED


def next_question():
    global question_index, game_over, feedback
    question_index += 1
    feedback = ""

    if question_index >= len(current_questions):
        game_over = True
        auth.save_high_score(current_user, score)
    else:
        load_question()


def draw():
    if game_state == "login":
        screen.fill(NAVY)
        title = title_font.render("2000's Trivia Challenge", True, GOLD)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        
        username_box.draw(screen)
        password_box.draw(screen)
        
        login_btn.draw(screen)
        register_btn.draw(screen)
        guest_btn.draw(screen)
        
        if auth_message:
            msg_surface = small_font.render(auth_message, True, WHITE)
            screen.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, 440))
            
    elif game_state == "game":
        screen.fill(PURPLE)

        title = title_font.render("2000's Trivia Challenge", True, BLACK)
        screen.blit(title, (190, 30))

        if not game_over:
            q = current_questions[question_index]

            question_text = question_font.render(q["question"], True, BLACK)
            screen.blit(question_text, (150, 100))

            for btn in buttons:
                btn.draw(screen, btn.text == selected_option)

            next_button.draw(screen)

            score_text = option_font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (650, 20))
            
            user_text = small_font.render(f"Player: {current_user}", True, BLACK)
            screen.blit(user_text, (20, 20))

            if feedback:
                shadow = feedback_font.render(feedback, True, BLACK)
                text = feedback_font.render(feedback, True, feedback_color)
                rect = text.get_rect(center=(WIDTH // 2, 440))
                screen.blit(shadow, (rect.x + 3, rect.y + 3))
                screen.blit(text, rect)
        else:
            final = question_font.render(f"Final Score: {score}/{len(current_questions)}", True, BLACK)
            screen.blit(final, (250, 200))

            if score == len(current_questions):
                msg = "🏆 Perfect Score!"
            elif score >= max(1, len(current_questions) - 1):
                msg = "⭐ Great Job!"
            else:
                msg = "👍 Keep Practicing!"

            result = question_font.render(msg, True, BLACK)
            screen.blit(result, (260, 260))

    pygame.display.update()


running = True

while running:
    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if game_state == "login":
            username_box.handle_event(event)
            password_box.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                if login_btn.is_clicked(pos):
                    username = username_box.text.strip()
                    password = password_box.text.strip()
                    success, auth_message = auth.authenticate(username, password)
                    if success:
                        current_user = username
                        game_state = "home"
                        print(f"DEBUG: login successful for {username}; set game_state=home")
                        pygame.event.clear()
                        pygame.time.wait(80)
                        continue
                        
                elif register_btn.is_clicked(pos):
                    username = username_box.text.strip()
                    password = password_box.text.strip()
                    success, auth_message = auth.register_user(username, password)
                    if success:
                        current_user = username
                        game_state = "home"
                        print(f"DEBUG: registration successful for {username}; set game_state=home")
                        pygame.event.clear()
                        pygame.time.wait(80)
                        continue
                        
                elif guest_btn.is_clicked(pos):
                    current_user = "Guest"
                    game_state = "home"
                    print("DEBUG: guest selected; set game_state=home")
                    pygame.event.clear()
                    pygame.time.wait(80)
                    continue
                    
        elif game_state == "home":
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if home_start_btn.is_clicked(pos):
                    start_game()
                    game_state = "game"
                elif home_tutorial_btn.is_clicked(pos):
                    game_state = "tutorial"
                elif home_logout_btn.is_clicked(pos):
                    # simple logout: go back to login screen
                    current_user = "Guest"
                    username_box.text = ""
                    password_box.text = ""
                    auth_message = "Signed out."
                    game_state = "login"

        elif game_state == "tutorial":
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if tutorial_start_btn.is_clicked(pos):
                    start_game()
                    game_state = "game"
                elif tutorial_back_btn.is_clicked(pos):
                    game_state = "home"

        elif game_state == "game" and not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                for btn in buttons:
                    if btn.is_clicked(pos):
                        selected_option = btn.text

                if next_button.is_clicked(pos) and selected_option:
                    check_answer()
                    draw()
                    pygame.time.delay(1200)
                    next_question()

pygame.quit()
sys.exit()