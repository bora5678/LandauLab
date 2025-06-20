from sample.Experiment import find_initial_frequency, measurement


if __name__ == '__main__':
    """Main function that runs everything."""
    i = find_initial_frequency()
    print(f"Initial frequency: {i} Hz")
    f = measurement()
    print(f"Final frequency: {f} Hz")