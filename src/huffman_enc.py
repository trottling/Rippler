import heapq
import pickle
import tempfile


class HuffmanNode:
    def __init__(self, freq, byte = None, left = None, right = None):
        self.freq = freq
        self.byte = byte
        self.left = left
        self.right = right

    # Чтобы heapq мог сравнивать узлы
    def __lt__(self, other):
        return self.freq < other.freq


class Huffman:
    def __build_huffman_tree(self, freq_table):
        heap = [HuffmanNode(f, byte=b) for b, f in freq_table.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)

        return heap[0] if heap else None

    def __build_codes(self, node, prefix = "", code_table = None):
        if code_table is None:
            code_table = { }
        if node is None:
            return code_table
        if node.byte is not None:
            code_table[node.byte] = prefix
        else:
            self.__build_codes(node.left, prefix + "0", code_table)
            self.__build_codes(node.right, prefix + "1", code_table)
        return code_table

    def encode_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            if not data:
                return None, "Файл пустой"

            # Подсчёт частот байтов
            freq_table = { }
            for b in data:
                freq_table[b] = freq_table.get(b, 0) + 1

            # Строим дерево и коды
            tree = self.__build_huffman_tree(freq_table)
            codes = self.__build_codes(tree)

            # Кодируем данные в битовую строку
            bitstring = "".join(codes[b] for b in data)
            # Дополняем нулями до полного байта
            padding = (8 - len(bitstring) % 8) % 8
            bitstring += "0" * padding

            # Переводим в байты
            encoded_bytes = bytearray()
            for i in range(0, len(bitstring), 8):
                byte = bitstring[i:i + 8]
                encoded_bytes.append(int(byte, 2))

            # Сохраняем дерево + padding + encoded data
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".huff")
            with open(tmp_file.name, "wb") as f:
                pickle.dump((tree, padding, encoded_bytes), f)

            return tmp_file.name, None
        except Exception as e:
            return None, str(e)

    def decode_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                tree, padding, encoded_bytes = pickle.load(f)

            # Переводим байты обратно в битовую строку
            bitstring = "".join(f"{b:08b}" for b in encoded_bytes)
            if padding:
                bitstring = bitstring[:-padding]

            # Декодирование
            result_bytes = bytearray()
            node = tree
            for bit in bitstring:
                node = node.left if bit == "0" else node.right
                if node.byte is not None:
                    result_bytes.append(node.byte)
                    node = tree

            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            with open(tmp_file.name, "wb") as f:
                f.write(result_bytes)

            return tmp_file.name, None
        except Exception as e:
            return None, str(e)
