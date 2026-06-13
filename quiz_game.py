import pygame
import sys

pygame.init()


WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Quiz Master 🚀")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 180, 255)
GREEN = (80, 220, 120)
RED = (255, 80, 80)
GRAY = (220, 220, 220)


title_font = pygame.font.SysFont("arial", 36, bold=True)
question_font = pygame.font.SysFont("arial", 28)
option_font = pygame.font.SysFont("arial", 24)


questions = [
    {
        "question": "What planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Venus", "Jupiter"],
        "answer": "Mars"
    },
    {
        "question": "Which animal is called the King of the Jungle?",
        "options": ["Tiger", "Elephant", "Lion", "Bear"],
        "answer": "Lion"
    },
    {
        "question": "What is 5 + 7?",
        "options": ["10", "11", "12", "13"],
        "answer": "12"
    },
    {
        "question": "Which language is used for this game?",
        "options": ["Java", "Python", "C++", "HTML"],
        "answer": "Python"
    },
    {
        "question": "How many days are there in a week?",
        "options": ["5", "6", "7", "8"],
        "answer": "7"
    },
    {
        "question": "What is the capital of France?",
        "options": ["London", "Paris", "Berlin", "Madrid"],
        "answer": "Paris"
    }
]

question_index = 0
score = 0
selected_option = None
game_over = False



class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface, selected=False):
        color = GREEN if selected else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        txt = option_font.render(self.text, True, BLACK)
        surface.blit(
            txt,
            (self.rect.x + 10, self.rect.y + 10)
        )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def create_buttons():
    buttons = []
    start_y = 150

    for i in range(4):
        btn = Button(200, start_y + i * 60, 400, 45, "")
        buttons.append(btn)

    return buttons

buttons = create_buttons()


next_button = Button(620, 420, 150, 50, "NEXT")
buttons = create_buttons()



def load_question():
    global selected_option, game_over

    # safety check (VERY IMPORTANT)
    if question_index >= len(questions):
        game_over = True
        return

    selected_option = None

    q = questions[question_index]

    for i in range(4):
        buttons[i].text = q["options"][i]


# ---------------- DRAW SCREEN ---------------- #
def draw():
    screen.fill(WHITE)

    # Title
    title = title_font.render("🚀 Galaxy Quiz Master 🚀", True, BLACK)
    screen.blit(title, (180, 30))

    if not game_over:

        q = questions[question_index]   

        next_button.draw(screen)

        # Question
        q_text = question_font.render(q["question"], True, BLACK)
        screen.blit(q_text, (50, 100))

        # Options
        for btn in buttons:
            btn.draw(screen, btn.text == selected_option)

        # Score
        score_text = option_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (650, 20))

    else:
        msg = f"Final Score: {score}/{len(questions)}"

        if score == len(questions):
            msg2 = "🏆 Amazing! Quiz Champion!"
        elif score >= 3:
            msg2 = "⭐ Great Job!"
        else:
            msg2 = "👍 Keep Practicing!"

        t1 = question_font.render(msg, True, BLACK)
        t2 = question_font.render(msg2, True, BLACK)

        screen.blit(t1, (250, 200))
        screen.blit(t2, (250, 260))

    pygame.display.update()

# ---------------- NEXT QUESTION ---------------- #
def next_question():
    global question_index, score, game_over

    # safety check
    if question_index >= len(questions):
        game_over = True
        return

    correct = questions[question_index]["answer"]

    if selected_option == correct:
        score += 1

    question_index += 1

    if question_index >= len(questions):
        game_over = True
    else:
        load_question()


# ---------------- MAIN LOOP ---------------- #
load_question()

running = True
while running:
    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pos = pygame.mouse.get_pos()

            # Check option clicks
            for btn in buttons:
                if btn.is_clicked(pos):
                    selected_option = btn.text

            # Next question click area (bottom right)
            next_rect = pygame.Rect(620, 420, 150, 50)

            if next_rect.collidepoint(pos):
                if selected_option is not None:
                    next_question()

    # Draw NEXT button
    if not game_over:
        pygame.draw.rect(screen, BLUE, (620, 420, 150, 50))
        txt = option_font.render("NEXT", True, BLACK)
        screen.blit(txt, (660, 435))

    pygame.time.delay(50)

pygame.quit()