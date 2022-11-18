def main():
    outside()
    inside(5)

def outside():
    global word, new 
    word = "new"
    new = "fort"
def inside(num):
    print(str(num)+word+new)

if __name__ == "__main__":
    main()
