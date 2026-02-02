import pyttsx3
import difflib
import json
import os
import sympy as sp
import re
import qrcode

from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ================== FILES ==================
FILE_NAME = "./retroai/knowledge.json"
os.makedirs("./retroai", exist_ok=True)

with open(FILE_NAME, "r", encoding="utf-8") as f:
    knowledge = json.load(f)

for key in ["meta", "personal", "tft", "archive", "generated"]:
    knowledge.setdefault(key, {})

def save_knowledge():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, indent=4, ensure_ascii=False)

# ================== VOICE ==================
def speak(text):
    print("AI:", text)
    engine = pyttsx3.init("sapi5")
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# ================== MATH ==================
def is_equation(text):
    return "=" in text and re.search(r"[0-9]", text)

def is_math_question(text):
    if is_equation(text):
        return True
    return bool(re.search(r"[0-9+\-*/^()]", text))


def solve_math(text):
    try:
        if "=" in text:
            left, right = text.split("=")
            expr = sp.Eq(sp.sympify(left), sp.sympify(right))
            solutions = sp.solve(expr)

            if solutions:
                return [f"The equation is {expr}", f"Solution: {solutions}"]
            else:
                return ["No solution found."]
        else:
            expr = sp.sympify(text)
            result = sp.simplify(expr)
            return [f"The expression is {expr}", f"Final answer is {result}"]
    except Exception as e:
        return ["Sorry, I couldn't solve this math problem."]
#-------------------------------- QR CODE ==================

def make_qrcode(data):
    img = qrcode.make(data)
    img.save("qrcode.png")
    return "qrcode.png"

# ================== INTENT ==================
def wants_details(text):
    return any(k in text.lower() for k in ["explain", "details", "more", "how"])

def is_learning_request(text):
    return any(k in text.lower() for k in ["teach", "learn", "remember"])

# ================== CLASSIFICATION ==================
def classify_question(text):
    lower = text.lower()
    if is_math_question(text):
        return "math"
    if any(w in lower for w in ["tft", "trait", "item", "comp", "augment", "build"]):
        return "tft"
    return "personal"

# ================== KNOWLEDGE EXPANSION ==================
def expand_knowledge():
    questions = list(knowledge["personal"].keys())
    answers = list(knowledge["personal"].values())

    if len(questions) < 2:
        return

    corpus = [q + " " + a for q, a in zip(questions, answers)]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(X)

    for i in range(len(questions)):
        for j in range(i + 1, len(questions)):
            if similarity[i][j] > 0.8:
                merged = answers[i] + " " + answers[j]
                knowledge["generated"][questions[i]] = merged

# ================== MATCHING ==================
def smart_match(user_input, keys):
    best = difflib.get_close_matches(user_input, keys, n=1, cutoff=0.6)
    if best:
        return best[0]

    for k in keys:
        if SequenceMatcher(None, user_input, k).ratio() > 0.75:
            return k
    return None

# ================== START ==================
speak("Hello! I'm Retro. I learn, infer, and grow smarter over time. Type exit to quit.")

while True:
    raw_input = input("You: ").strip()
    user_input = raw_input.lower()

    if user_input == "exit":
        expand_knowledge()
        save_knowledge()
        speak("Goodbye! My knowledge has expanded.")
        break
    # ---------- SIMPLE QR ----------
    if "qr" in user_input or "qrcode" in user_input or "كيو" in user_input:
        speak("give me the link for QR code")
        data = input("QR: ").strip()

        file_name = make_qrcode(data)
        speak(f"QR code created successfully as {file_name}")
        continue

    # ---------- Math ----------
    if is_math_question(raw_input):
        for step in solve_math(raw_input):
            speak(step)
        continue

    category = classify_question(user_input)
    source = knowledge["tft"] if category == "tft" else knowledge["personal"]

    all_keys = list(source.keys()) + list(knowledge["generated"].keys())
    match = smart_match(user_input, all_keys)

    if match:
        if match in knowledge["generated"]:
            speak(knowledge["generated"][match])
        else:
            answer = source[match]

            if isinstance(answer, dict):
                if wants_details(user_input):
                    speak(answer.get("details", answer.get("short")))
                else:
                    speak(answer.get("short"))
            else:
                speak(answer)
    else:
        speak("I don't know that yet. Do you want to teach me?")
        teach = input("(yes/no): ").strip().lower()

        if teach == "yes":
            new_answer = input("Type the answer: ").strip()
            speak("Are you sure this information is correct?")
            confirm = input("(yes/no): ").strip().lower()

            if confirm == "yes":
                source[user_input] = new_answer
                save_knowledge()
                speak("Got it. I learned something new.")
            else:
                speak("Okay, I won't save it.")
        else:
            speak("Alright.")
# ================== END ==================




