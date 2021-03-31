import argparse, io, re
from pdfreader import PDFDocument
from pprint import pprint
import asn1

import OpenSSL

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", help="Input file: To be signed PDF.", required=True, type=argparse.FileType("rb"))
parser.add_argument("-c", "--certfile", help="Output file: The cerificate inside the PDF.", required=True, type=argparse.FileType("wb"))
parser.add_argument("-s", "--signaturefile", help="Output file: The signature inside the PDF.", required=True, type=argparse.FileType("wb"))
parser.add_argument("-b", "--byterangefile", help="Output file: The byterangefile content of the PDF.", required=True, type=argparse.FileType("wb"))

args = parser.parse_args()

infile = args.infile
certfile = args.certfile
signaturefile = args.signaturefile
byterangefile = args.byterangefile

pdf = PDFDocument(infile)
rootentry = pdf.obj_by_ref(pdf.trailer.root)
certinfo = rootentry["Perms"]["DocMDP"]

cert = certinfo["Cert"]
signature = certinfo["Contents"]
certfile.write(cert)
mybytes = str(signature)
signaturefile.write(bytearray.fromhex(mybytes))

byterange = certinfo["ByteRange"]

print(byterange)

infile.seek(byterange[0], 0)
byterangefile.write(infile.read(byterange[1]))

infile.seek(byterange[2], 0)
byterangefile.write(infile.read(byterange[3]))

infile.seek(byterange[0], 0)
message = infile.read(byterange[1])

infile.seek(byterange[2], 0)
message += infile.read(byterange[3])

#message = str(message)
#message = message.encode('utf-8')

test = open("testbin.pdf", "wb")
test.write(message)
test.close()

decoder = asn1.Decoder()
decoder.start(signature.to_bytes())
tag, real_signature = decoder.read()

x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
pubkey = x509.get_pubkey()
print("Pubkey", pubkey.type(), OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pubkey))
print("Signature", real_signature.hex())
validate = OpenSSL.crypto.verify(x509, real_signature, message, 'sha1')

#print("Check Signature", validate)
infile.close()
certfile.close()
signaturefile.close()


print()
print(str(signature))