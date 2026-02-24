import random
from word_list import word


class Hangman:

    def __init__(self, category, difficulty="Medium"):
        self.category = category
        self.secret_word = random.choice(word[category])
        self.guessed = []
        self.score = 0
        self.hint_used = False

        # Difficulty setup
        if difficulty == "Easy":
            self.max_lives = 8
        elif difficulty == "Hard":
            self.max_lives = 4
        else:
            self.max_lives = 6

        self.lives = self.max_lives
        self.difficulty = difficulty

    # ---------------- GUESS LETTER ---------------- #

    def guess(self, letter):
        if letter in self.guessed or self.lives <= 0:
            return

        self.guessed.append(letter)

        if letter in self.secret_word:
            self.score += 10
        else:
            self.lives -= 1
            self.score -= 5

    # ---------------- USE HINT ---------------- #

    def use_hint(self):
        if self.hint_used or self.lives <= 1:
            return False

        for letter in self.secret_word:
            if letter not in self.guessed:
                self.guessed.append(letter)
                self.lives -= 1
                self.hint_used = True
                return True

        return False

    # ---------------- DISPLAY WORD ---------------- #

    def display_word(self):
        return " ".join(
            [l if l in self.guessed else "_" for l in self.secret_word]
        )

    # ---------------- GAME OVER CHECK ---------------- #

    def is_over(self):
        return (
            self.lives <= 0 or
            all(letter in self.guessed for letter in self.secret_word)
        )