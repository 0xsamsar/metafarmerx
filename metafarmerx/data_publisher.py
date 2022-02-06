from adapters.api_adapter import CGAdapter, HomoraAdapter, CreamAdapter

def main():
    price = CGAdapter()
    farming_apy = HomoraAdapter()
    borrowing_apy = CreamAdapter()

    print(price.call())
    print(farming_apy.call())
    print(borrowing_apy.call())

if __name__ == "__main__":
    main()
    