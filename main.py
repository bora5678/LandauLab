from sample.Experiment import find_initial_frequency, measurement


if __name__ == '__main__':
    """Main function that runs everything."""
    i, f = measurement()
    print(f"Initial frequency: {i} Hz")
    print(f"Final frequency: {f} Hz")