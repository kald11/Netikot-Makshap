from core.google_sheets import GoogleSheets


def main():
    df = GoogleSheets().get_data()
    print(df.values)
    print("maor")


if __name__ == "__main__":
    main()
