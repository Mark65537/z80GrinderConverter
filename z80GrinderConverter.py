import argparse
import os
import sys

templates_dir = "templates\\"

def check_file_size(file_name):
    max_size = 8 * 1024
    file_size = os.path.getsize(file_name)
    
    if file_size > max_size:
        print(f"Warning: The converted file ({file_name}) should not exceed 8KB in size.")
        
def write_data_to(file_name, data, type='dac'):
    base_name = os.path.splitext(file_name)[0]

    if type == 'dac':
        output_file_name = f"{base_name}_{type}.asm"
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
        # max_size = 8 * 1024
        # template_size = os.path.getsize(f"{templates_dir}DAC.bin")
        # if (template_size + len(data)) < max_size:
            # with open(f"{templates_dir}DAC.bin", "rb") as temp_file:
            #     template_data = temp_file.read()

        output_file_name = f"{base_name}.{type}"
        with open(output_file_name, "wb") as file_out:
            # if (template_size + len(data)) < max_size:
            #     file_out.write(template_data)
            file_out.write(bytes(data))

        check_file_size(output_file_name)
    
            
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

    id = file_in.read(4).decode()  # Assuming the file is opened in binary mode
    chunk_size1 = int.from_bytes(file_in.read(4), 'little') # read_int32(file_in)
    format_code = int.from_bytes(file_in.read(2), 'little') # read_int16(file_in)
    channels = int.from_bytes(file_in.read(2), 'little')
    sample_rate = int.from_bytes(file_in.read(4), 'little')
    bytes_per_second = int.from_bytes(file_in.read(4), 'little')
    bytes_per_sample = int.from_bytes(file_in.read(2), 'little')
    bits_per_sample = int.from_bytes(file_in.read(2), 'little')

    if id != "fmt ":
        print("Unknown chunk id " + id)
        return 0

    print("              ID:", id)
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
    data=read_headers_and_return_data(file_name)
    # Choose the type based on the output_type parameter
    if output_type == 'bin':
        write_data_to(file_name, data, type='bin')
    else:
        write_data_to(file_name, data)

def read_headers_and_return_data(file_name):
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
            return data


def wav2java(input_file_path):
    file_format = os.path.splitext(input_file_path)[1]
    if file_format != ".wav":
        print(f"Invalid file format: {file_format}. Expected .wav format.")
        return
    
    # Get the base name without extension
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    
    # Define constants
    max_int_size = 32 * 1024 + 180
    max_byte_size = 8 * 1024
    template_size = os.path.getsize(f"{templates_dir}DAC.bin")
    
    # Get input file size and read headers
    input_file_size = os.path.getsize(input_file_path)
    data = read_headers_and_return_data(input_file_path)
    data_size = len(data)

    if (template_size + data_size) > max_int_size:
        # Split data into chunks and write to files
        for i in range(0, data, max_int_size):
            chunck_data = data[i:i+max_int_size]
            write_data_to(f'{base_name}{i//max_int_size}', chunck_data, type='bin')
            bin2java(f"{base_name}{i//max_int_size}.bin")
    elif (template_size + data_size) <= max_byte_size:
        write_data_to(f'{base_name}', data, type='bin')
        bin2java(f"{base_name}.bin", data_array_type='byte')

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

    
def bin2java(input_file_path, data_array_type='int', output_file_path=None):
    class_name = os.path.splitext(os.path.basename(input_file_path))[0]  # Get the base name without extension
    if output_file_path is None:
        output_file_path = f"{class_name}.java"

    try:
        with open(input_file_path, "rb") as file_in:
            data = file_in.read()

        file_size = len(data)

        with open(output_file_path, "w") as file_out:
            file_out.write(f"package res.music;\n\n")
            file_out.write(f"public class {class_name}\n{{\n")
            file_out.write("  public static void Init() {}\n\n")
            file_out.write(f"  public static {data_array_type}[] z80_code =\n  {{\n")
            for i in range(0,file_size, 4):
                if i % 24 == 0:
                    file_out.write("\n   ") 

                if data_array_type == 'int':
                    bytes_to_write = data[i:i+4]  # Get 4 bytes at a time
                    int_value = int.from_bytes(bytes_to_write, byteorder='big')  # Convert bytes to integer
                    file_out.write(f"0x{int_value:08x}, ")
                elif data_array_type == 'byte':
                    if data[i] > 127:
                        file_out.write(f"{data[i] - 256}, ")
                    else:
                        file_out.write(f"{data[i]}, ")
                else:
                    print(f"Invalid data type: {data_array_type}")
                    sys.exit(1)
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

def main():
    parser = argparse.ArgumentParser(
        description="Convert files between different formats: wav, dac, bin, java."
    )

    parser.add_argument(
        '-in', 
        dest='input_format', 
        required=True, 
        help="Input format (e.g., wav, bin, java)"
    )
    parser.add_argument(
        '-out', 
        dest='output_format', 
        required=True, 
        help="Output format (e.g., dac, bin, java)"
    )
    parser.add_argument(
        'file_name', 
        help="The name of the file to be converted"
    )

    args = parser.parse_args()

    input_format = args.input_format
    output_format = args.output_format
    in_file_name = args.file_name
    
    # Add checks for formats and call the respective function based on the input and output formats
    if input_format == "wav" and output_format == "dac" or output_format == "asm":
        wav2file(in_file_name, output_type='dac')
    elif input_format == "wav" and output_format == "bin":
        wav2file(in_file_name, output_type='bin')
    elif input_format == "wav" and output_format == "java":
        wav2java(in_file_name)
    elif input_format == "bin" or input_format == "ram" and output_format == "java":
        bin2java(in_file_name)
    elif input_format == "bin" and output_format == "wav":
        bin2wav(in_file_name)
    elif input_format == "java" and output_format == "bin":
        java2bin(in_file_name)
    elif input_format == "java" and output_format == "wav":
        java2wav(in_file_name)
    else:
        print("Unsupported format conversion.")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()