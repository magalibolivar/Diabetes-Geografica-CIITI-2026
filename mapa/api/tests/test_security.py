from mapa import security


def test_la_clave_generada_se_verifica_y_no_se_guarda_en_claro():
    key = security.generate_key()
    assert key.plaintext.startswith("mk_")
    assert key.plaintext not in key.key_hash
    assert security.parse_prefix(key.plaintext) == key.prefix
    assert security.verify_key(key.plaintext, key.key_hash)


def test_una_clave_distinta_no_verifica():
    a, b = security.generate_key(), security.generate_key()
    assert not security.verify_key(a.plaintext, b.key_hash)


def test_prefijo_malformado():
    for raw in ("", "mk_", "xx_abcd_123", "mk_abcd", "mk_a_b_c"):
        assert security.parse_prefix(raw) is None


def test_alcances():
    assert security.scope_allows(["read"], "read")
    assert not security.scope_allows(["read"], "read:draft")
    assert security.scope_allows(["read:draft"], "read")  # draft incluye read
    assert not security.scope_allows([], "read")
