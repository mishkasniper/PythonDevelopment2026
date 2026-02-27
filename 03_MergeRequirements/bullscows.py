import random
import sys
import urllib.request

def bullscows(ans: str, que: str) -> tuple[int, int]:
    if len(ans) != len(que):
        print(f"answer {ans} has a different length, true length is a {len(que)}")
        return (None, None)
    
    ans_used = [False] * len(ans)
    que_used = [False] * len(que)
    
    bulls, cows = 0, 0

    for i, (g, s) in enumerate(zip(ans, que)):
        if g == s:
            bulls += 1
            ans_used[i] = True
            que_used[i] = True

    for i, g in enumerate(ans):
        if ans_used[i]:
            continue
        for j, s in enumerate(que):
            if not que_used[j] and g == s:
                cows += 1
                que_used[j] = True
                break

    return (bulls, cows)

def gameplay(ask: callable, inform: callable, words: list[str]) -> int:
    length = len(words[0])
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

def load_dict(source: str, length: int = None) -> list[str]:
    if source.startswith(('http://', 'https://')):
        with urllib.request.urlopen(source) as response:
            data = response.read().decode('utf-8')
            words = data.splitlines()
    else:
        try:
            with open(source, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            words = source.split(',') if ',' in source else [source]
    
    if length:
        words = [w for w in words if len(w) == length]
    
    return words

def main():
    if len(sys.argv) < 2:
        print("Use: python -m bullscows <dictionary> [len]")
        sys.exit(1)
    
    dictionary = sys.argv[1]
    length = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    words = load_dict(dictionary, length)

    if not words:
        print("list of words empty")
        return 0
    
    iter = gameplay(ask, inform, words)

    print(iter)

if __name__ == "__main__":
    main()



    
    