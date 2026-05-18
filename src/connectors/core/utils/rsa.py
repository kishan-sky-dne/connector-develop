"""
__author__ = "Sky UK Ltd"
__copyright__ = Copyright © Sky CP Limited 2023.
All rights reserved. No part of this work may be reproduced,
stored in a retrieval system of any nature, or transmitted,
in any form or by any means including photocopying
and recording, without the prior written permission of Sky,
the copyright owner.
__licence__ = "subject to the terms of the licence with Sky UK Ltd'
__version__ = "1.0"
"""

# Standard Library
import logging

# Third Party Library
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA as CRYPTO_RSA
from Crypto.PublicKey.RSA import RsaKey

# DNE Library
from connectors.core.config.connectors_config import config

logger = logging.getLogger(__name__)


class RSA:
    def __init__(self) -> None:
        logger.debug("Retrieving public and private keys from config")
        logger.debug(f"Public key is: {config.get('rsa', 'public_key')}")
        logger.debug(f"Public key repr is: {repr(config.get('rsa', 'public_key'))}")
        self.PUBLIC_KEY: RsaKey = CRYPTO_RSA.import_key(config.get("rsa", "public_key").encode())
        self.__PRIVATE_KEY: RsaKey = CRYPTO_RSA.import_key(config.get("rsa", "private_key").encode())

    def encrypt(self, data: str) -> str:
        """
        Encrypts a given string using the rsa public key

        Args:
            data (str): plain text data to be encrypted

        Returns:
            str: cipher text encrypted using rsa
        """
        logger.debug("Encrypting data using rsa public key")

        cipher_rsa = PKCS1_OAEP.new(self.PUBLIC_KEY)
        self.cipher_text = cipher_rsa.encrypt(data.encode()).decode("latin1")
        return self.cipher_text

    def decrypt(self, data: bytes) -> str:
        """
        Decrypts a given string using the rsa private key

        Args:
            data (bytes): cipher text encrypted using rsa

        Returns:
            str: decrypted plain text
        """
        logger.debug("Decrypting data using rsa private key")

        cipher_rsa = PKCS1_OAEP.new(self.__PRIVATE_KEY)
        self.plain_text = cipher_rsa.decrypt(data).decode()
        return self.plain_text
