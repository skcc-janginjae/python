from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Replace these with your actual Modulus and Exponent values
modulus = int(
    "BFE4B1DD88BCF8A4CE35E1B2521F33D31B531B03828D690A86ACD524790C62D270A678082EFF5386EEC765E6B4200DAE624C412352BDB83B921CFF64E9252A934FEDED973D0D85D0854AA78B37684867BBA754CE6D0452E9D944B71EAAD21FCE24C6CF3595408F890A99135978CB341848E1CC1D921A975F77E038D7920D7985AF9AAA1B8D55C7D9661572234F568C803615F3330A5B7F96C83649F42AA2B10FC3B060C4FDE3E2391C78C31FB3405876AF97303C535EAE7C716325AE94843D5CB18826954BD1C91AE9999A4EFE302DC36EBDC1F49DEA97E87358C33127084269FDAE5D04C59664FCAC9EF0AA8B02B130B6D1F3F407E1C0F3A71CB80DEF949E11", 16
)
exponent = 65537

# Generate the RSA public key
public_numbers = rsa.RSAPublicNumbers(exponent, modulus)
public_key = public_numbers.public_key(default_backend())

# Save the public key in PEM format
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print(pem.decode())
