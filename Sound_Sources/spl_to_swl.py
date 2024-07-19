import math


def convert_spl_to_swl(spl_db_c, distance_m):
    """
    Convert SPL (dB(C)) at a given distance to Sound Power Level (SWL).

    Parameters:
    spl_db_c (float): Sound Pressure Level in dB(C)
    distance_m (float): Distance at which the SPL was measured in meters

    Returns:
    float: Sound Power Level in dB
    """
    # Calculate SWL using the formula: L_W = L_p + 20 * log10(r) + 11
    swl_db = spl_db_c + 20 * math.log10(distance_m) + 11
    return swl_db


def save_to_central_file(source_name, spl_db_c, distance_m, swl_db, filename="sound_sources_info.txt"):
    """
    Save the sound source information to a centralized text file.

    Parameters:
    source_name (str): Name of the sound source
    spl_db_c (float): Sound Pressure Level in dB(C)
    distance_m (float): Distance at which the SPL was measured in meters
    swl_db (float): Sound Power Level in dB
    filename (str): The name of the centralized text file
    """
    with open(filename, 'a') as file:
        file.write(f"Sound Source: {source_name}\n")
        file.write(f"SPL (dB(C)): {spl_db_c}\n")
        file.write(f"Distance (meters): {distance_m}\n")
        file.write(f"Sound Power Level (SWL) in dB: {swl_db:.2f}\n")
        file.write("-----------------------------------------------------\n")
    print(f"Information appended to {filename}")


if __name__ == "__main__":
    # Input the name of the sound source, SPL in dB(C), and distance in meters
    source_name = input("Enter the name of the sound source: ")
    spl_db_c = float(input("Enter SPL in dB(C): "))
    distance_m = float(input("Enter distance in meters: "))

    # Convert SPL to SWL
    swl_db = convert_spl_to_swl(spl_db_c, distance_m)

    # Display the result
    print(f"Sound Power Level (SWL) is: {swl_db:.2f} dB")

    # Save the information to a centralized file
    save_to_central_file(source_name, spl_db_c, distance_m, swl_db)
