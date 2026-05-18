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
from unittest.mock import Mock, patch

# DNE Library
from connectors.core.utils.rsa import RSA


@patch("connectors.core.utils.rsa.config")
@patch("connectors.core.utils.rsa.CRYPTO_RSA")
def setup(crypto_rsa_mock, conf_mock) -> tuple[RSA, Mock, Mock]:
    private_key_mock = Mock()
    public_key_mock = Mock()
    crypto_rsa_mock.import_key.side_effect = [public_key_mock, private_key_mock]
    conf_mock.get.side_effect = ["public_key", "public_key", "public_key", "private_key"]

    rsa_obj = RSA()

    return rsa_obj, public_key_mock, private_key_mock


def test_constructor():
    rsa_obj, public_key_mock, private_key_mock = setup()

    assert rsa_obj.__dict__ == {"PUBLIC_KEY": public_key_mock, "_RSA__PRIVATE_KEY": private_key_mock}


@patch("connectors.core.utils.rsa.PKCS1_OAEP")
def test_encrypt(
    pkcs1_oaep_mock,
):
    rsa_obj, public_key_mock, private_key_mock = setup()
    rsa_cipher = Mock()
    pkcs1_oaep_mock.new.return_value = rsa_cipher
    rsa_cipher.encrypt.return_value.decode.return_value = b"cipher_text"

    assert rsa_obj.encrypt("plain_text") == b"cipher_text"
    pkcs1_oaep_mock.new.assert_called_once_with(public_key_mock)
    rsa_cipher.encrypt.assert_called_once_with("plain_text".encode())
    rsa_cipher.encrypt.return_value.decode.assert_called_once_with("latin1")


@patch("connectors.core.utils.rsa.PKCS1_OAEP")
def test_decrypt(
    pkcs1_oaep_mock,
):
    rsa_obj, public_key_mock, private_key_mock = setup()
    rsa_cipher = Mock()
    pkcs1_oaep_mock.new.return_value = rsa_cipher
    rsa_cipher.decrypt.return_value.decode.return_value = "plain_text"

    assert rsa_obj.decrypt(b"cipher_text") == "plain_text"
    pkcs1_oaep_mock.new.assert_called_once_with(private_key_mock)
    rsa_cipher.decrypt.assert_called_once_with(b"cipher_text")
    rsa_cipher.decrypt.return_value.decode.assert_called_once_with()
