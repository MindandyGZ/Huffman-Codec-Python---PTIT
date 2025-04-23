import heapq
import struct
import codecs
from typing import Optional, Union, List, Dict
from node import HuffmanNode
from fcpair import FrequencyCharPair

_BITORDER = 'little'
_TERMINATOR = FrequencyCharPair(0, None)

def encode(data: Union[str, bytes], ofile_name: Optional[str] = None) -> Optional[bytes]:
    """
    Mã hóa dữ liệu (văn bản hoặc nhị phân) sử dụng mã hóa Huffman.
    
    Args:
        data: Dữ liệu cần mã hóa (chuỗi văn bản hoặc bytes)
        ofile_name: Tên file đầu ra (tùy chọn)
        
    Returns:
        Dữ liệu đã mã hóa dưới dạng bytes nếu không có tên file đầu ra
    """
    # Chuyển đổi dữ liệu thành bytes nếu là chuỗi văn bản
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    fc_pairs = _getFrequencyCharPairs(data)
    tree = _createTree(fc_pairs)
    binary_map = _getBinaryMap(tree)

    header_buffer = _encodeFrequencyCharPairs(fc_pairs)
    data_buffer = _encodeData(data, binary_map)

    if ofile_name:
        with open(ofile_name, "wb") as ofile:
            ofile.write(header_buffer + data_buffer)
        return None
    else:
        return header_buffer + data_buffer

def decode(byte_data: bytes, ofile_name: Optional[str] = None) -> Optional[Union[str, bytes]]:
    """
    Giải mã dữ liệu đã được mã hóa Huffman.
    
    Args:
        byte_data: Dữ liệu đã mã hóa dưới dạng bytes
        ofile_name: Tên file đầu ra (tùy chọn)
        
    Returns:
        Dữ liệu đã giải mã (chuỗi văn bản hoặc bytes)
    """
    char_byte_count, freq_count, freq_byte_count = struct.unpack_from(_modifyTypeFormat("IIB"), byte_data, 0)
    offset = 9

    freq_buffer = byte_data[offset:offset + (freq_count * freq_byte_count)]
    offset += freq_count * freq_byte_count
    frequencies = _decodeFrequencies(freq_buffer, freq_byte_count)

    char_buffer = byte_data[offset:offset + char_byte_count]
    offset += char_byte_count
    fc_pairs = _decodeFrequencyCharPairs(char_buffer, frequencies)

    tree = _createTree(fc_pairs)
    decoded_data = _decodeDataBytes(byte_data[offset:], tree)

    if ofile_name:
        with open(ofile_name, "wb") as ofile:
            ofile.write(decoded_data)
        return None
    else:
        return decoded_data

def encodeFile(ifile_name: str, ofile_name: Optional[str] = None) -> Optional[bytes]:
    """
    Mã hóa file sử dụng mã hóa Huffman.
    
    Args:
        ifile_name: Tên file đầu vào
        ofile_name: Tên file đầu ra (tùy chọn)
        
    Returns:
        Dữ liệu đã mã hóa dưới dạng bytes nếu không có tên file đầu ra
    """
    with open(ifile_name, "rb") as f:
        data = f.read()
    return encode(data, ofile_name)

def decodeFile(ifile_name: str, ofile_name: Optional[str] = None) -> Optional[Union[str, bytes]]:
    """
    Giải mã file đã được mã hóa Huffman.
    
    Args:
        ifile_name: Tên file đầu vào đã mã hóa
        ofile_name: Tên file đầu ra (tùy chọn)
        
    Returns:
        Dữ liệu đã giải mã (chuỗi văn bản hoặc bytes)
    """
    with open(ifile_name, "rb") as f:
        byte_data = f.read()
    return decode(byte_data, ofile_name)

def _createTree(frequency_char_pairs):
    heap = list(frequency_char_pairs)
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(left.frequency + right.frequency, left, right)
        heapq.heappush(heap, merged)

    return heap[0]

def _getFrequencyCharPairs(data: bytes):
    """
    Tính toán tần suất xuất hiện của các byte trong dữ liệu.
    
    Args:
        data: Dữ liệu dưới dạng bytes
        
    Returns:
        Danh sách các cặp (tần suất, byte)
    """
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    pairs = [FrequencyCharPair(f, c) for c, f in freq.items()]
    return _formatFrequencyCharPairs(pairs, sort=True)

def _getBinaryMap(node):
    bin_map = {}
    stack = [(node, "")]

    while stack:
        current, path = stack.pop()
        if isinstance(current, HuffmanNode):
            stack.append((current.rightChild, path + "1"))
            stack.append((current.leftChild, path + "0"))
        else:
            bin_map[current.character] = path
    return bin_map

def _encodeData(data: bytes, binary_map: Dict[int, str]) -> bytes:
    """
    Mã hóa dữ liệu bytes sử dụng bảng mã nhị phân.
    
    Args:
        data: Dữ liệu cần mã hóa
        binary_map: Bảng mã nhị phân
        
    Returns:
        Dữ liệu đã mã hóa dưới dạng bytes
    """
    if not binary_map:
        return bytearray()

    res = bytearray()
    byte = 0
    bit_count = 0

    for b in data:
        bit_str = binary_map[b]

        for bit in bit_str:
            if bit == "1":
                byte = _setBit(byte, bit_count)
            bit_count += 1
            if bit_count == 8:
                res.append(byte)
                byte = 0
                bit_count = 0

    if bit_count:
        res.append(byte)
    return res

def _encodeFrequencyCharPairs(pairs):
    """
    Mã hóa thông tin về tần suất và byte.
    
    Args:
        pairs: Danh sách các cặp (tần suất, byte)
        
    Returns:
        Dữ liệu đã mã hóa dưới dạng bytes
    """
    freq_count = len(pairs) - 1
    freq_byte_count = (pairs[freq_count].frequency.bit_length() + 7) // 8
    freq_buffer = bytearray()
    char_buffer = bytearray()

    for pair in pairs:
        if pair.character is not None:
            char_buffer.append(pair.character)
            freq_buffer.extend(pair.frequency.to_bytes(freq_byte_count, _BITORDER))

    header = struct.pack(_modifyTypeFormat("IIB"), len(char_buffer), freq_count, freq_byte_count)
    return header + freq_buffer + char_buffer

def _decodeFrequencyCharPairs(char_buffer, frequencies):
    """
    Giải mã thông tin về tần suất và byte.
    
    Args:
        char_buffer: Buffer chứa các byte
        frequencies: Danh sách tần suất
        
    Returns:
        Danh sách các cặp (tần suất, byte)
    """
    if len(char_buffer) != len(frequencies):
        raise ValueError("Character and frequency lengths mismatch")

    pairs = [FrequencyCharPair(freq, char) for freq, char in zip(frequencies, char_buffer)]
    return _formatFrequencyCharPairs(pairs, sort=False)

def _decodeFrequencies(freq_buffer, freq_byte_count):
    """
    Giải mã thông tin về tần suất.
    
    Args:
        freq_buffer: Buffer chứa dữ liệu tần suất
        freq_byte_count: Số byte cho mỗi tần suất
        
    Returns:
        Danh sách tần suất
    """
    if freq_byte_count <= 0 or freq_byte_count > 4:
        raise ValueError("Invalid frequency byte count")

    return [_convertBytesToInt(freq_buffer[i:i+freq_byte_count]) for i in range(0, len(freq_buffer), freq_byte_count)]

def _decodeDataBytes(data_bytes, root):
    """
    Giải mã dữ liệu bytes.
    
    Args:
        data_bytes: Dữ liệu đã mã hóa
        root: Gốc của cây Huffman
        
    Returns:
        Dữ liệu đã giải mã dưới dạng bytes
    """
    res = bytearray()
    node = root

    for byte in data_bytes:
        for bit in range(8):
            node = node.rightChild if _getBit(byte, bit) else node.leftChild
            if not isinstance(node, HuffmanNode):
                if node.character is None:
                    return bytes(res)
                res.append(node.character)
                node = root

    return bytes(res)

def _formatFrequencyCharPairs(pairs, sort):
    pairs.append(_TERMINATOR) if sort else pairs.insert(0, _TERMINATOR)
    return sorted(pairs) if sort else pairs

def _modifyTypeFormat(fmt):
    return ("<" if _BITORDER == 'little' else ">") + fmt

def _setBit(byte, bit):
    return byte | (1 << (7 - bit))

def _getBit(byte, bit):
    return (byte >> (7 - bit)) & 1

def _convertBytesToInt(b):
    return int.from_bytes(b.ljust(4, b'\0'), _BITORDER)
