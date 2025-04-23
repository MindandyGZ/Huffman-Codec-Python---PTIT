import argparse
import os
from encoder import encodeFile, decodeFile

def getFileSize(filename):
    try:
        size = os.path.getsize(filename)
        if size < 1000:
            return size, "B"
        elif size < 1_000_000:
            return size / 1000, "KB"
        else:
            return size / 1_000_000, "MB"
    except FileNotFoundError:
        printErrorExit(f"The file '{filename}' does not exist")
    except IOError:
        printErrorExit(f"Unable to access the file '{filename}'")

def printStatistics(ifile_name, ifile_size, ofile_name, ofile_size, show_compression):
    separator = "=" * 80
    section = "-" * 80

    print(separator)
    print("File Statistics")
    print(separator)

    print("Input File")
    print(section)
    print(f"Name: {ifile_name}")
    print(f"File Size: {ifile_size[0]:.2f} {ifile_size[1]}\n")

    print("Output File")
    print(section)
    print(f"Name: {ofile_name}")
    print(f"File Size: {ofile_size[0]:.2f} {ofile_size[1]}")

    if show_compression and ifile_size[0] != 0:
        percent = 100 * (1 - (ofile_size[0] / ifile_size[0]))
        print(f"File Compressed: {percent:.2f}%")

def printErrorExit(msg, error_code=2):
    print("[ERROR]:", msg)
    exit(error_code)

def createArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Text file to encode or binary file to decode")
    parser.add_argument("-o", "--ofile", help="Output file name", default=None)
    parser.add_argument("-e", "--encode", action="store_true", help="Encode the input file")
    parser.add_argument("-d", "--decode", action="store_true", help="Decode the input file")
    return parser

def main():
    parser = createArgParser()
    args = parser.parse_args()

    ofile = args.ofile or f"{os.path.splitext(args.input_file)[0]}.out"
    ifile_size = getFileSize(args.input_file)
    show_compression = False

    try:
        if args.encode and args.decode:
            printErrorExit("Cannot both encode and decode a single file.")
        elif args.decode:
            decodeFile(args.input_file, ofile)
        else:
            encodeFile(args.input_file, ofile)
            show_compression = True
    except (FileNotFoundError, IOError):
        printErrorExit(f"Failed to process file '{args.input_file}'")

    ofile_size = getFileSize(ofile)
    printStatistics(args.input_file, ifile_size, ofile, ofile_size, show_compression)

if __name__ == "__main__":
    main()
