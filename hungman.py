import random
from pathlib import Path

MAX_ATTEMPTS = 6

HANGMAN_STAGES = [
    """
     +---+
     |   |
         |
         |
         |
        ===
    """,
    """
     +---+
     |   |
     O   |
         |
         |
        ===
    """,
    """
     +---+
     |   |
     O   |
     |   |
         |
        ===
    """,
    """
     +---+
     |   |
     O   |
    /|   |
         |
        ===
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
        ===
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
        ===
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
        ===
    """
]


def load_words():
    """Load valid words from words.txt."""
    file_path = Path(__file__).with_name("words.txt")

    with open(file_path, "r", encoding="utf-8") as file:
        words = [
            word.strip().upper()
            for word in file
            if word.strip().isascii()
            and word.strip().isalpha()
            and 4 <= len(word.strip()) <= 12
        ]

    if not words:
        raise ValueError("No valid words found in words.txt.")

    return words


def display_word(secret_word, guessed_letters):
    """Show guessed letters and hide the remaining letters."""
    return " ".join(
        letter if letter in guessed_letters else "_"
        for letter in secret_word
    )


def play_hangman():
    try:
        secret_word = random.choice(load_words())
    except FileNotFoundError:
        print("Error: words.txt not found.")
        print("Place words.txt in the same folder as hangman.py.")
        return
    except ValueError as error:
        print(f"Error: {error}")
        return

    guessed_letters = set()
    wrong_guesses = 0

    print("\n" + "=" * 36)
    print("       WELCOME TO HANGMAN")
    print("=" * 36)
    print("Guess the hidden word one letter at a time!")
    print(f"You have {MAX_ATTEMPTS} incorrect guesses available.")

    while wrong_guesses < MAX_ATTEMPTS:
        print(HANGMAN_STAGES[wrong_guesses])
        print("Word:", display_word(secret_word, guessed_letters))
        print(
            "Guessed letters:",
            ", ".join(sorted(guessed_letters)) or "None"
        )
        print("Attempts remaining:", MAX_ATTEMPTS - wrong_guesses)

        if all(letter in guessed_letters for letter in secret_word):
            print("\n" + "=" * 36)
            print("       CONGRATULATIONS!")
            print("          YOU WIN!")
            print("=" * 36)
            print("The word was:", secret_word)
            return

        guess = input("\nEnter a letter: ").strip().upper()

        if len(guess) != 1 or not guess.isascii() or not guess.isalpha():
            print("Invalid input. Please enter one English letter.")
            continue

        if guess in guessed_letters:
            print("You already guessed that letter. No penalty!")
            continue

        guessed_letters.add(guess)

        if guess in secret_word:
            print("Correct! The letter is in the word.")
        else:
            wrong_guesses += 1
            print("Incorrect! You lost one attempt.")

    print(HANGMAN_STAGES[MAX_ATTEMPTS])
    print("\n" + "=" * 36)
    print("          GAME OVER!")
    print("=" * 36)
    print("The correct word was:", secret_word)
    print("Better luck next time!")


if __name__ == "__main__":
    play_hangman()