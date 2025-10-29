#!/usr/bin/env python3
import re
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
QUESTION_DIR = BASE_DIR / 'questionnaire'

QUESTION_RE = re.compile(r'^\s*(\d+)\.\s*(.+)$')
CHOICE_RE = re.compile(r'^\s*([A-Za-z])\s*[\)\.\-:]\s*(.+?)(?:\s*([✔✓]))?\s*$')
IDENT_MARK = "🆔"

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
SEPARATOR = "\n===========================\n"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def list_txt_files_recursive(folder):
    if not folder.exists() or not folder.is_dir():
        return []
    return sorted([p for p in folder.rglob('*.txt') if p.is_file()])

def display_path(p):
    try:
        return str(p.relative_to(QUESTION_DIR))
    except Exception:
        return p.name

def choose_file(files):
    print(f"\nFound {len(files)} .txt file(s) under: {QUESTION_DIR.resolve()}\n")
    for i, f in enumerate(files, start=1):
        print(f"{i}) {display_path(f)}")
    while True:
        choice = input(f"\nSelect file by number (1-{len(files)}): ").strip()
        if not choice.isdigit():
            print("Enter a valid number.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(files):
            return files[idx - 1]
        print("Number out of range.")

def parse_questions(text):
    lines = text.splitlines()
    questions = []
    current = None
    for line in lines:
        if not line.strip():
            continue
        qm = QUESTION_RE.match(line)
        if qm:
            if current:
                questions.append(current)
            q_text = qm.group(2).strip()
            is_ident = q_text.endswith(IDENT_MARK)
            ident_answer = None
            if is_ident:
                q_text = q_text.replace(IDENT_MARK, '').strip()
                if '.' in q_text:
                    parts = q_text.split('.', 1)
                    question_part = parts[0].strip()
                    ident_answer = parts[1].strip()
                    q_text = question_part
            current = {
                'num': qm.group(1),
                'question': q_text,
                'choices': {},
                'correct': None,
                'is_ident': is_ident,
                'ident_answer': ident_answer
            }
            continue
        cm = CHOICE_RE.match(line)
        if cm and current is not None and not current['is_ident']:
            letter = cm.group(1).lower()
            choice = cm.group(2).strip()
            is_check = bool(cm.group(3))
            current['choices'][letter] = choice
            if is_check:
                current['correct'] = letter
            continue
        if current is not None:
            if not current['choices'] and not current['is_ident']:
                current['question'] += ' ' + line.strip()
            elif current['choices']:
                last = sorted(current['choices'].keys())[-1]
                current['choices'][last] += ' ' + line.strip()
    if current:
        questions.append(current)
    return questions

def ask_and_grade(questions):
    results = []
    score = 0
    total = len(questions)
    for q in questions:
        print(SEPARATOR)
        print(f"{q['num']}. {q['question']}")
        if q['is_ident']:
            ans = input("\nAnswer? (Identification): ").strip()
            correct_ans = q['ident_answer']
            if correct_ans and ans.lower() == correct_ans.lower():
                print(f"{GREEN}✅ Correct!{RESET}")
                score += 1
                is_correct = True
            else:
                print(f"{RED}❌ Incorrect.{RESET}")
                print(f"   Correct answer: {GREEN}{correct_ans}{RESET}")
                is_correct = False
        else:
            for letter in sorted(q['choices'].keys()):
                print(f"  {letter}) {q['choices'][letter]}")
            valid = set(q['choices'].keys())
            prompt = f"\nAnswer? ({'/'.join(sorted(valid))}): "
            while True:
                ans = input(prompt).strip().lower()
                if ans == '':
                    print("Please enter a letter.")
                    continue
                ans_letter = ans[0]
                if ans_letter in valid:
                    break
                else:
                    print(f"Invalid choice. Enter one of: {', '.join(sorted(valid))}")
            correct = q.get('correct')
            is_correct = (correct is not None and ans_letter == correct)
            if is_correct:
                print(f"{GREEN}✅ Correct!{RESET}")
                score += 1
            else:
                if correct is None:
                    print(f"{YELLOW}⚠️  No answer key found for this question (no checkmark).{RESET}")
                    print(f"   Your answer: {ans_letter}) {q['choices'].get(ans_letter)}")
                else:
                    print(f"{RED}❌ Incorrect.{RESET}")
                    print(f"   Correct answer: {GREEN}{correct}) {q['choices'][correct]}{RESET}")
        results.append({
            'num': q['num'],
            'question': q['question'],
            'selected': ans,
            'correct': q['ident_answer'] if q['is_ident'] else q.get('correct'),
            'is_correct': is_correct,
            'is_ident': q['is_ident']
        })
    print(SEPARATOR)
    print(f"Finished. Score: {score} / {total}")
    print("\nSummary:")
    for r in results:
        if r['is_correct']:
            status = f"{GREEN}Correct{RESET}"
        else:
            status = f"{RED}Incorrect{RESET}"
        if r['is_ident']:
            print(f"{r['num']}. (Identification) Your: {r['selected']} | Correct: {r['correct']} | Result: {status}")
        else:
            print(f"{r['num']}. Your: {r['selected']} | Correct: {r['correct']} | Result: {status}")
    return results, score, total

def main():
    files = list_txt_files_recursive(QUESTION_DIR)
    if not files:
        print(f"No .txt files found in: {QUESTION_DIR.resolve()}")
        sys.exit(1)
    selected = choose_file(files)
    try:
        raw = selected.read_text(encoding='utf-8')
    except Exception as e:
        print("Failed to read file:", e)
        sys.exit(1)
    questions = parse_questions(raw)
    clear_console()
    if not questions:
        print("No questions parsed. Ensure numbered questions like '1. Question...' and choices like 'a) Option'.")
        sys.exit(1)
    has_key = sum(1 for q in questions if q.get('correct') or q['is_ident'])
    print(f"\nFound {len(questions)} questions. {has_key} question(s) have an answer key detected.")
    try:
        ask_and_grade(questions)
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(0)

if __name__ == '__main__':
    main()
