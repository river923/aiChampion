from secretstore.crypto import decrypt_secret, encrypt_secret


def test_encrypt_secret_when_round_trip() -> None:
    plain_text = "sk-demo-secret"

    encrypted = encrypt_secret(plain_text)

    assert encrypted != plain_text
    assert decrypt_secret(encrypted) == plain_text
