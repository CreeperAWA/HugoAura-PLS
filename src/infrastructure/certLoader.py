from pathlib import Path
import ssl
from loguru import logger
import datetime
import ipaddress

from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

import lifecycle
from services.config import updateConfig
from typeDefs.config import AuraPLSConfig


def generateSelfSignedCert(userConfig: AuraPLSConfig):
    if userConfig.regenCert:
        privateKey = ec.generate_private_key(ec.SECP256R1())

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(
                    NameOID.COMMON_NAME, "HugoAura - This cert is generated locally"
                ),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "HugoAura Devs"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Aura PLS"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, "HA"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(privateKey.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("*.hugoaura.local"),
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    ]
                ),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )
            .sign(privateKey, hashes.SHA512())
        )

        try:
            with open(
                Path.joinpath(lifecycle.plsDataDir, Path(userConfig.certPath)),
                "wb",
            ) as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
        except:
            logger.error(
                "❌ Failed to generate self-signed cert: certPath inaccessible or not found."
            )
            return False

        try:
            with open(
                Path.joinpath(lifecycle.plsDataDir, Path(userConfig.keyPath)),
                "wb",
            ) as f:
                f.write(
                    privateKey.private_bytes(
                        serialization.Encoding.PEM,
                        serialization.PrivateFormat.TraditionalOpenSSL,
                        serialization.NoEncryption(),
                    )
                )
        except:
            logger.error(
                "❌ Failed to generate self-signed cert: keyPath inaccessible or not found."
            )
            return False

        logger.success("🔐 Successfully generated self-signed certificate.")
        updateConfig("regenCert", False)
        return True
    else:
        return


def createSSLContext(userConfig, type):
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if type == "ws":
            ssl_context.load_cert_chain(
                Path.joinpath(lifecycle.plsDataDir, Path(userConfig.certPath)),
                keyfile=Path.joinpath(lifecycle.plsDataDir, Path(userConfig.keyPath)),
            )
            return ssl_context
        else:
            logger.error(f"Unknown TLS certs type: {type}")
            return None
    except Exception as e:
        logger.error(f"Error reading TLS certs: {e}")
        return None
