import os
import sys
import numpy
import hashlib

valid_hashes = [
	# PyTorch Checkpoint V1:
	"f856e9d99c30855d6ead4d00cc3a5573",
	"d9dbfbea61309dc1e087f5081e98331a",
	"2b2bed47912ceb828c0a37aac4b99073",
	"ea0405cdb5bc638fee12de614f729ebc",
	"4babdbd05b8923226a9e9622492054b6",
	# PyTorch Checkpoint V2:
	"d9dbfbea61309dc1e087f5081e98331a",
	"f856e9d99c30855d6ead4d00cc3a5573",
	"4babdbd05b8923226a9e9622492054b6",
	"ea0405cdb5bc638fee12de614f729ebc",
	"2b2bed47912ceb828c0a37aac4b99073",
	# HuggingFace Checkpoint V1:
	"d0e13331c103453e9e087d59dcf05432",
	"29aae4d31a0a4fe6906353001341d493",
	"b40838eb4e68e087b15b3d653ca1f5d7",
	"f845ecc481cb92b8a0586c2ce288b828",
	"f3b13d089840e6caf22cd6dd05b77ef0",
	"12e0d2d7a9c00c4237b1b0143c48a05e",
	"1348f7c8bb3ee4408b69305a10bdfafb",
	"aee09e21813368c49baaece120125ae3",
	"eeec4125e9c7560836b4873b6f8e3025",
	"598538f18fed1877b41f77de034c0c8a",
	"fdb311c39b8659a5d5c1991339bafc09",
	"b77e99aa2ddc3df500c2b2dc4455a6af",
	"edd1a5897748864768b1fab645b31491",
	"6b2e0a735969660e720c27061ef3f3d3",
	# HuggingFace Checkpoint V2:
	"5cfcb78b908ffa02e681cce69dbe4303",
	"3eddc6fc02c0172d38727e5826181adb",
	"fecfda4fba7bfd911e187a85db5fa2ef",
	"6b2e0a735969660e720c27061ef3f3d3",
	"d566f98b28bf74ce6b35d5b20a651b27",
	"148bfd184af630a7633b4de2f41bfc49",
	"e1dc8c48a65279fb1fbccff14562e6a3",
	"fdb311c39b8659a5d5c1991339bafc09",
	"eeec4125e9c7560836b4873b6f8e3025",
	"edd1a5897748864768b1fab645b31491",
	"99762d59efa6b96599e863893cf2da02",
	"9cffb1aeba11b16da84b56abb773d099",
	"462a2d07f65776f27c0facfa2affb9f9",
	"92754d6c6f291819ffc3dfcaf470f541",
]

def hash_file(fn):
	return hashlib.md5(open(fn, "rb").read()).hexdigest()

def cipher_file(dst, src_payload, hash_base, block_size=4096):
	hash_base = bytearray(hash_base)
	hash_base = hash_base * (4096 / len(hash_base))
	buf2 = numpy.array(hash_base, dtype=numpy.uint8)
	fp_payload = open(src_payload, 'rb')
	with open(dst, 'wb') as fp:
		while True:
			buf1 = numpy.array(bytearray(fp_payload.read(block_size)), dtype=numpy.uint8)
			buf = numpy.bitwise_xor(buf1, buf2[:len(buf1)])
			fp.write(buf)
			if len(buf1) < block_size: break
	fp_payload.close()

def hash_dir(src):
	for path in os.listdir(src):
		if hash_file("%s/%s" % (src, path)) in valid_hashes:
			print("[*] Verification successful.")
			return True
	return False

def cipher_dir(dst, src_payload, hash_base):
	for path in os.listdir(src_payload):
		print("[*] Processing '%s'" % path)
		cipher_file("%s/%s" % (dst, path), "%s/%s" % (src_payload, path), hash_base)

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print("Usage: hash_codec.py <DESTINATION> <PAYLOAD SOURCE> <LLAMA SOURCE>")
		exit()
	dst = sys.argv[1]
	src_payload = sys.argv[2]
	src_base = sys.argv[3]
	if (src_base in valid_hashes) or hash_dir(src_base):
		src_base = valid_hashes[0]
	else:
		print("[!] Verification failed.")
		exit()
	cipher_dir(dst, src_payload, src_base)
