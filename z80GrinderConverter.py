import os
import sys

templates_dir = "templates\\"
def write_data_to(file_name, data, type='dac'):
    base_name = os.path.splitext(file_name)[0]
    if type == 'dac':
        with open(f"{base_name}_{type}.asm", "w") as file_out:
            for i in range(len(data)):
                if i % 8 == 0:
                    file_out.write("\n  db")
                d = f"${data[i]:02x}"
                if i % 8 == 0:
                    file_out.write(" " + d)
                else:
                    file_out.write(", " + d)
    elif type == 'bin':
        with open(f"{templates_dir}DAC.bin", "rb") as temp_file:
            template_data = temp_file.read()
        with open(f"{base_name}.{type}", "wb") as file_out:
            file_out.write(template_data)
            file_out.write(bytes(data))
    
            
def read_data_header(file_in):
    print("Data Header:")

    id = file_in.read(4).decode()  
    if id == '\x00\x00da': # Почему то иногда битность(bitsPerSample) содержиться в 4 байтах из за этого заоловок data сдвигается на 2 байта
        file_in.seek(-2, 1)
        id = file_in.read(4).decode()

    chunk_size = int.from_bytes(file_in.read(4), 'little')
    if id != "data":
        print("Unknown chunk id", id)
        return 0
    print("              ID:", id)
    print("      Chunk Size:", chunk_size)
    return chunk_size


    # base_name = os.path.splitext(file_in.name)[0]
    # with open(base_name + "_dac.asm", "w") as file_out:
    #     for i in range(len(data)):
    #         if i % 8 == 0:
    #             file_out.write("\n  db")
                
    #         d = "0x{:02x}".format(data[i])
    #         if i % 8 == 0:
    #             file_out.write(" " + d)
    #         else:
    #             file_out.write(", " + d)
    # return chunk_size

def write_data_header(file_out, chunk_size):
    print("Data Header:")

    id='data'
    file_out.write(id.encode())  
    file_out.write(chunk_size.to_bytes(4, 'little'))

    print("              ID:", id)
    print("      Chunk Size:", chunk_size)
    return chunk_size

def read_fmt_header(file_in):
    print("FMT Header:")

    id_ = file_in.read(4).decode()  # Assuming the file is opened in binary mode
    chunk_size1 = int.from_bytes(file_in.read(4), 'little') # read_int32(file_in)
    format_code = int.from_bytes(file_in.read(2), 'little') # read_int16(file_in)
    channels = int.from_bytes(file_in.read(2), 'little')
    sample_rate = int.from_bytes(file_in.read(4), 'little')
    bytes_per_second = int.from_bytes(file_in.read(4), 'little')
    bytes_per_sample = int.from_bytes(file_in.read(2), 'little')
    bits_per_sample = int.from_bytes(file_in.read(2), 'little')

    if id_ != "fmt ":
        print("Unknown chunk id " + id_)
        return 0

    print("              ID:", id_)
    print("      Chunk Size:", chunk_size1)
    print("     Format Code:", format_code)
    print("         Channels:", channels)
    print("     Sample Rate:", sample_rate)
    print("Bytes Per Second:", bytes_per_second)
    print("Bytes Per Sample:", bytes_per_sample)
    print(" Bits Per Sample:", bits_per_sample)

    if bits_per_sample != 8 or channels != 1:
        print("This wav isn't in the right format.")
        return 0

    return chunk_size1

def write_fmt_header(file_out):
    print("FMT Header:")

    id = "fmt "
    chunk_size1 = 18
    format_code = 1
    channels = 1
    # sample_rate = 11025
    # sample_rate = 3973 # PlayTitleSample rate (DAC rate)
    sample_rate = 872
    bits_per_sample = 8
    bytes_per_second = sample_rate * channels
    # bytes_per_second = sample_rate * bits_per_sample * channels
    bytes_per_sample = channels
    # bytes_per_sample = bits_per_sample * channels

    file_out.write(id.encode())
    file_out.write(chunk_size1.to_bytes(4, 'little'))
    file_out.write(format_code.to_bytes(2, 'little'))
    file_out.write(channels.to_bytes(2, 'little'))
    file_out.write(sample_rate.to_bytes(4, 'little'))
    file_out.write(bytes_per_second.to_bytes(4, 'little'))
    file_out.write(bytes_per_sample.to_bytes(2, 'little'))
    file_out.write(bits_per_sample.to_bytes(4, 'little'))

    print("              ID:", id)
    print("      Chunk Size1:", chunk_size1)
    print("     Format Code:", format_code)
    print("         Channels:", channels)
    print("     Sample Rate:", sample_rate)
    print("Bytes Per Second:", bytes_per_second)
    print("Bytes Per Sample:", bytes_per_sample)
    print(" Bits Per Sample:", bits_per_sample)

def read_riff_header(file_in):
    print("RIFF Header:")

    id = file_in.read(4).decode()
    if id != "RIFF":
        print("Not a RIFF file.")
        return 0
    wav_size = int.from_bytes(file_in.read(4), 'little')
    format = file_in.read(4).decode()
    if format != "WAVE":
        print("Not a WAV file.")
        return 0
    
    print("              ID:", id)
    print("            Size:", wav_size)
    print("          Format:", format)
    return wav_size

def write_riff_header(file_out, chunk_size):
    print("RIFF Header:")

    id = b'RIFF'
    wav_size = 44 + chunk_size
    format = b'WAVE'

    file_out.write(id)
    file_out.write(wav_size.to_bytes(4, 'little'))
    file_out.write(format)

    print("              ID:", id)
    print("            Size:", wav_size)
    print("          Format:", format)

def wav2file(file_name, output_type='dac'):
    with open(file_name, 'rb') as file:
        if read_riff_header(file) == 0:
            return
        if read_fmt_header(file) == 0:
            return

        chunk_size = read_data_header(file)
        if chunk_size == 0:
            return
        else:
            data = bytearray(chunk_size)
            file.readinto(data)
            # Choose the type based on the output_type parameter
            if output_type == 'bin':
                write_data_to(file.name, data, type='bin')
            else:
                write_data_to(file.name, data)

def wav2java(input_file_path):
    file_format = os.path.splitext(input_file_path)[1]
    if file_format != ".wav":
        print(f"Invalid file format: {file_format}. Expected .wav format.")
        return
    
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]  # Get the base name without extension    
    wav2file(input_file_path, 'bin')
    bin2java(f"{base_name}.bin")

def bin2wav(file_name):
    
    chunk_size = os.path.getsize(file_name)
    if chunk_size == 0:
            print(f"File {file_name} is empty")
            return

    with open(file_name, 'rb') as source:
        data = source.read()     # Чтение содержимого исходного файла
    
    base_name = os.path.splitext(file_name)[0]
    with open(f"{base_name}.wav", 'wb') as file:
        write_riff_header(file, chunk_size)
        write_fmt_header(file)
        write_data_header(file, chunk_size)
        file.write(data)

    
def bin2java(input_file_path, output_file_path=None):
    class_name = os.path.splitext(os.path.basename(input_file_path))[0]  # Get the base name without extension
    if output_file_path is None:
        output_file_path = f"{class_name}.java"

    try:
        with open(input_file_path, "rb") as file_in:
            data = file_in.read()

        file_size = len(data)

        with open(output_file_path, "w") as file_out:
            file_out.write(f"public class {class_name}\n{{\n")
            file_out.write("  public static byte[] z80_code =\n  {\n")
            for i in range(file_size):
                if i % 8 == 0:
                    file_out.write("\n   ") # New line every 8 bytes

                if data[i] > 127:
                    file_out.write(f"{data[i] - 256}, ")
                else:
                    file_out.write(f"{data[i]}, ")
            file_out.write("\n  };\n")
            file_out.write("}\n")

    except Exception as e:
        print(e)
        sys.exit(1)

def java2bin(input_file_path, output_file_path=None):

    # if len(sys.argv) == 3:
    #     bin_file_name = sys.argv[2]
    # else:
    #     dot_index = java_file_name.rfind(".")
    #     if dot_index != -1:
    #         bin_file_name = java_file_name[:dot_index] + ".bin"
    #     else:
    #         bin_file_name = java_file_name + ".bin"

    class_name = os.path.splitext(os.path.basename(input_file_path))[0]  # Get the base name without extension
    if output_file_path is None:
        output_file_path = f"{class_name}.bin"

    try:
        with open(input_file_path, "r") as java_file:
            java_file_content = java_file.read()


        start = java_file_content.find("{", java_file_content.find("{") + 1)
        end = java_file_content.find("}")
        byte_string = java_file_content[start+1:end]
        byte_string = byte_string.replace("\n", "").replace(" ", "")

        byte_values = byte_string.split(",")
        data = bytearray()

        for byte_value in byte_values:
            if byte_value:
                byte_int = int(byte_value)
                if byte_int < 0:
                    byte_int += 256                   
                data.append(byte_int)


        with open(output_file_path, "wb") as bin_file:
            bin_file.write(data)
    except Exception as e:
        print(e)
        sys.exit(1)

    print(f"INFO: Binary file '{output_file_path}' created successfully")

def java2wav(input_file_path, output_file_path=None):
    file_format = os.path.splitext(input_file_path)[1]
    if file_format != ".java":
        print(f"Invalid file format: {file_format}. Expected .java format.")
        return
    
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]  # Get the base name without extension    
    java2bin(input_file_path)
    bin2wav(f"{base_name}.bin")

def show_help():
    help_message = """
    INFO: bin2java - Copyright 2023 by Mark6    
    Usage: [script] -in <input_format> -out <output_format> <file_name>

    This script supports conversion between the following formats: wav, dac, bin, java

    Examples:
    [script] -in bin -out java somefile.bin    # Convert from BIN to Java
    [script] -in java -out bin somefile.java   # Convert from Java to BIN
    [script] -in wav -out bin somefile.wav     # Convert from WAV to BIN
    [script] -in dac -out bin somefile_dac.asm     # Convert from DAC to BIN
    ... and so on for other supported format conversions.
    """
    print(help_message)

if __name__ == "__main__":
    if len(sys.argv) < 5 or '-h' in sys.argv or '--help' in sys.argv:
        show_help()
        sys.exit(0)


    # Parse the command line arguments
    try:
        input_index = sys.argv.index("-in") + 1
        output_index = sys.argv.index("-out") + 1
        in_file_name = sys.argv[5]
        input_format = sys.argv[input_index]
        output_format = sys.argv[output_index]
    except (ValueError, IndexError):
        show_help()
        sys.exit(1)
    
    # Add checks for formats and call the respective function based on the input and output formats
    if input_format == "wav" and output_format == "dac" or output_format == "asm":
        wav2file(in_file_name, output_type = 'dac')
    elif input_format == "wav" and output_format == "bin":
        wav2file(in_file_name, output_type = 'bin')
    elif input_format == "wav" and output_format == "java":
        wav2java(in_file_name)
    elif input_format == "bin" and output_format == "java":
        bin2java(in_file_name)
    elif input_format == "bin" and output_format == "wav":
        bin2wav(in_file_name)
    elif input_format == "java" and output_format == "bin":
        java2bin(in_file_name)
    elif input_format == "java" and output_format == "wav":
        java2wav(in_file_name)
    # Additional format checks and function calls can be added here based on new functions.
    else:
        print("Unsupported format conversion.")
        show_help()