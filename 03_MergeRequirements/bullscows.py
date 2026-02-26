import random
import sys
import urllib.request

def bullscows(ans: str, que: str) -> tuple[int, int]:
    if len(ans) != len(que):
        print(f"answer {ans} has a different length, true length is a {len(que)}")
        return (None, None)
    
    bulls, cows = 0, 0
    i = 0
    while i < len(ans):
        if ans[i] == que[i]:
            bulls += 1
            ans.pop(i)
            que.pop(i)
            i -= 1
        i += 1

    i, j = 0, 0
    while i < len(ans):
        while j < len(que):
            if ans[i] == que[j]:
                cows += 1
                ans.pop(i)
                que.pop(j)
                i -= 1
                j -= 1
            j += 1
        i += 1

    return (bulls, cows)

def gameplay(ask: callable, inform: callable, words: list[str]) -> int:
    length = words[0]
    for elem in words:
        if len(elem) != length:
            print("words in list must be same length")
            return 0

    b, c = 0, 0
    iter = 0
    question = random.choice(words)
    while b != len(question):
        answer = ask("Введите слово: ", words)
        b, c = bullscows(answer, question)
        if (b, c) == (None, None):
            continue
        inform("Быки: {}, Коровы: {}", b, c)
        iter += 1

    return iter

def ask(prompt: str, valid: list[str] = None) -> str:
    if valid == None:
        print(prompt)
        return input()
    while True:
        print(prompt)
        answer = input()
        if answer in valid:
            return answer
        print("uncorrect word")

def inform(format_string: str, bulls: int, cows: int) -> None:
    print(format_string.format(bulls, cows))





    
    