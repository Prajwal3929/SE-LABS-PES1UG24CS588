# Project: Real-Time Endless Runner Game

This project is a terminal-based endless runner using **Pygame**. It introduces students to interactive game design using object-oriented principles and real-time graphical rendering.

---

## What’s Provided

A partially working version of an endless runner with:

- A player-controlled character that jumps over obstacles with gravity pulling it back down
- Obstacles that spawn at a regular interval and scroll toward the player, gradually speeding up
- Score display

You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**

---

## Getting Started

### Setup

1. Clone the repo or download the project folder.
2. Make sure you have Python 3.10+ installed.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the game:

```bash
python main.py
```




## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Refine Collision Detection

> The game speeds up forever with no limit, and once it's fast enough obstacles can zip past the player without the hit ever registering. Investigate and enhance collision accuracy (and/or the speed ramp) so it stays fair no matter how long a run lasts.


### Task 2: Implement Game Over Condition

> Add a screen that displays the final score once the player collides with an obstacle, then gracefully waits for input instead of just printing to the console.


### Task 3: Add Replay Option

> After Game Over, allow the user to play again by choosing a difficulty (Easy, Medium, or Hard starting speed/spawn rate), or exit.



### Task 4: Add Sound Feedback

> Add basic sound effects for jumping, passing an obstacle (scoring), and the game-over moment.



---

## Expected Behavior

- Player jumps with `Space`, `Up`, or `W`, and gravity brings it back down to the ground
- Obstacles spawn at a regular interval and scroll from right to left, gradually getting faster
- Score increases by one each time the player clears an obstacle
- Game ends when the player collides with an obstacle

---

## Folder Structure

```
endless-runner-main/
├── main.py
├── requirements.txt
├── game/
│   ├── game_engine.py
│   ├── player.py
│   └── obstacle.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history

